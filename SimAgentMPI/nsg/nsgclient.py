#!/usr/bin/env python
import sys
import os
import time
import shutil
import requests
import xml.etree.ElementTree as ET
import SimAgentMPI.nsg.pyjavaproperties as Props

# Flush stdout for debugging
sys.stdout.flush()

# Warning: you probably want to get rid of this line and follow the advice 
# here https://urllib3.readthedocs.org/en/latest/security.html.
requests.packages.urllib3.disable_warnings()

# verbose is enabled/disabled via property file.  See main() below.
verbose=True

def _prefixProperty(property, prefix):
    if property.startswith(prefix):
        return property
    return "%s%s" % (prefix, property)

class CipresError(Exception):
    def __init__(self, httpStatus, cipresCode, message, rawtext):
        self.httpStatus = httpStatus 
        self.cipresCode = cipresCode
        self.message = message
        self.rawtext = rawtext
        super(CipresError, self).__init__(self.message)

class ValidationError(CipresError):
    def __init__(self, httpStatus, cipresCode, message, fieldErrors, rawtext):
        super(ValidationError, self).__init__(httpStatus, cipresCode, message, rawtext)
        self.fieldErrors = fieldErrors
    def asString(self):
        str = self.message + "\n"
        for e in self.fieldErrors:
            str += "%s: %s\n" % (e, self.fieldErrors[e])
        return str

class Client(object):
    global verbose
    def __init__(self, appname, appID, username, password, baseUrl, endUserHeaders=None):
        """ baseUrl is something like https://host/cipresrest/v1 
            endUserHeaders are for applications that use umbrella authentication only.
        """
        self.appname = appname
        self.appID = appID
        self.username = username
        self.password = password
        self.baseUrl = baseUrl
        self.headers = {'cipres-appkey': self.appID }
        if endUserHeaders:
            self.endUsername = endUserHeaders.get('cipres-eu')
            if not self.endUsername or not endUserHeaders.get('cipres-eu-email'):
                raise Exception("endUserHeaders must include cipres-eu and cipres-eu-email")
            self.headers.update(endUserHeaders)
            self.endUsername = self.appname + "." + self.endUsername
        else:
            self.endUsername = self.username


    def listJobs(self):
        """ returns list of JobStatus objects """
        r = self.__doGet__(url=self.baseUrl + "/job/" + self.endUsername + "/?expand=true")
        return self.__parseJobList__(r.text)

    def getJobStatus(self, jobHandle):
        """ queries for status and returns JobStatus object """
        return JobStatus(client=self, jobUrl=self.baseUrl + "/job/" + self.endUsername + "/" + jobHandle)

    def submitJob(self, vParams, inputParams, metadata, validateOnly=False ):
        """ 
        Submits a job and returns a JobStatus object.   Raises ValidationException if submission isn't valid, 
        CipresException for other CIPRES problems (e.g. authorization, quotas), requests.exceptions.RequestException 
        for problems contacting CIPRES. 

        vparams is a dictionary where each key is a Visible parameter name, value is the string value to 
        assign the parameter. For example:
            {"toolId" : "CLUSTALW", "runtime_" : "1"}

        inputParams is a dictionary where each key is an InFile parameter name and the value is the full path of the 
        file.  For example:
            {"infile_" : "/samplefiles/sample1_in.fasta, "usetree_" : "/samplefiles/guidetree.dnd"}

        metadata is a dictionary of metadata params. For example:
            {"statusEmail" : "true"}

        See https://www.phylo.org/restusers/docs/guide.html#ConfigureParams for more info.
        """
        files = {}
        try:
            for key in inputParams:
                paramname = _prefixProperty(key, "input.")
                pathname = inputParams[key]
                files[paramname] = open(pathname, 'rb')
            payload = []
            if isinstance(vParams, dict):
                for key in vParams:
                    if key == "toolId" or key == "tool":
                        name = "tool"
                    else:
                        name = _prefixProperty(key, "vparam.");
                    payload.append((name, vParams[key]))
            else:
                for tuple in vParams:
                    if tuple[0] == "toolId" or tuple[0] == "tool":
                        name  = "tool"
                    else:
                        name = _prefixProperty(tuple[0], "vparam.")
                    payload.append((name, tuple[1]))
            if metadata:
                for key in metadata:
                    name = _prefixProperty(key, "metadata.");
                    payload.append((name, metadata[key]))

            if validateOnly:
                url = self.baseUrl + "/job/" + self.endUsername + "/validate"
            else:
                url = self.baseUrl + "/job/" + self.endUsername

            response = requests.post(url, data=payload, files=files, auth=(self.username, self.password), headers=self.headers, verify=False)
            if verbose:
                print("POSTED Payload of ", payload)
                print("POSTED file list of ", files)
                print("\n")
                print("POST Status = %d" % ( response.status_code))
                print("Response Content = %s" % (response.text))

            if response.status_code == 200:
                return JobStatus(self, xml=ET.fromstring(response.text.encode('utf-8')))
            else:
                self.__raiseException__(response)
        finally:
            for param, openfile in files.items():
                openfile.close
                

    def validateJob(self, vParams, inputParams, metadata ):
        """ Validates a job and returns  a JobStatus object where commandline is the only field set. 
            If job isn't valid, raises a ValidationError.
        """
        return self.submitJob(vParams, inputParams, metadata, validateOnly=True)

    def submitJobTemplate(self, testdir, metadata=None, validateOnly=False ):
        """
        Same as submitJob except that instead of using vParams and inputParams dictionaries
        you supply the name of a "job template" directory that contains 2 properties files,
        testParam.properties (which contains the vParams) and testInput.properties (which
        contains the inputParams).  The directory will also contain the input data files.
        For example, testParam.properties might look like: 
            toolId=CLUSTALW
            runtime_=.5
        and testInput.properties might look like:
            infile_=sample1_in.fasta
            usetree_=guidetree.dnd
        and the directory also contains files named sample1_in.fasta and guidetree.dnd.

        You can supply metadata via a dictionary argument, as with submitJob().
        """
        testdir = os.path.normpath(testdir) + os.sep
        fileParams = Props.Properties()
        with open(testdir + "input.properties") as infile:
            fileParams.load(infile)
        otherParams = Props.Properties()
        with open(testdir + "param.properties") as infile:
            otherParams.load(infile)

        for param in fileParams.propertyNames():
            pathname = fileParams.getProperty(param)
            if not os.path.isabs(pathname):
                pathname = os.path.join(testdir, os.path.basename(pathname))
            fileParams[param] = pathname 
        return self.submitJob(otherParams.getPropertyDictAsList(), fileParams.getPropertyDict(), metadata=metadata, validateOnly=validateOnly)

    def validateJobTemplate(self, testDir, metadata=None):
        return self.submitJobTemplate(testDir, metadata=metadata, validateOnly=True)


    def __raiseException__(self, response):
        """ Throws CipresException or ValidationException depending on the type of xml ErrorData 
        Cipres has returned. """

        httpStatus = response.status_code 
        if response.text and len(response.text) > 0:
            rawtext = response.text 
        else:
            rawtext = "No content returned." 

        # Parse displayMessage, code and fieldErrors from response.text
        displayMessage = None
        cipresCode = 0 
        fieldErrors = {}
        if response.text:
            try:
                element = ET.fromstring(response.text.encode('utf8')) 
                if element.tag == "error":
                    displayMessage = element.find("displayMessage").text
                    cipresCode = int(element.find("code").text)
                    if (cipresCode == 5):
                        for fieldError in element.findall("paramError"): 
                            fieldErrors[fieldError.find("param").text] = fieldError.find("error").text
            except Exception as e:
                pass

        # Show user the http status code and the <displayMessage> if available, otherwise the raw text.
        message = "HTTP Code: %d, " % (response.status_code)
        message += (rawtext, displayMessage)[displayMessage is not None]

        if (cipresCode and cipresCode == 5):
            raise ValidationError(httpStatus, cipresCode, message, fieldErrors, rawtext)
        else:
            raise CipresError(httpStatus, cipresCode, message, rawtext)


    def __doGet__(self, url, stream=False ,isdownload=False):
        """ Returns xml text or throws a CipresError """
        r = requests.get(url, auth=(self.username, self.password), verify=False, headers = self.headers, stream=stream);
        if verbose:
            if not isdownload:
                print("GET %s\nStatus = %d\nText:%s\n" % (url, r.status_code, r.text))
            else:
                print("Verbose logging for downloaded files suppressed in the code")
        if r.status_code != 200:
            self.__raiseException__(r);
        return r

    def __doDelete__(self, url):
        """ Returns nothing or throws a CipresError """
        r = requests.delete(url, auth=(self.username, self.password), verify=False, headers = self.headers);
        if r.status_code != 200 and r.status_code != 204 and r.status_code != 202:
            self.__raiseException__(r)
        if verbose:
            print("DELETE %s\nStatus = %d\nContent = %s" % (url, r.status_code, r.text))
        return r

    def __parseJobList__(self, text):
        """ Converts xml job listing to a list of JobStatus object """
        jobList = []
        et = ET.fromstring(text.encode('utf-8'))
        for xmlJobStatus in et.find("jobs"):
            jobList.append(JobStatus(client=self, xml=xmlJobStatus))
        return jobList
      
        

class JobStatus(object):
    """ Construct with jobUrl parameter and then call update() to fetch the status or construct with 
    xml parameter containing an element of type jobStatus and ctor will parse out the jobUrl """

    def __init__(self, client, jobUrl=None, xml=None):
        self.client = client 
        self.jobUrl = jobUrl
        self.__clear__()
        if xml is not None:
            self.__parseJobStatus__(xml)
        elif jobUrl is not None:
            self.jobUrl = jobUrl
            self.update()

    def __clear__(self):
        self.resultsUrl = None
        self.workingDirUrl = None
        self.jobHandle = None
        self.jobStage = None
        self.terminalStage = None
        self.failed = None
        self.metadata = None
        self.dateSubmitted = None
        self.messages = [ ] 
        self.commandline = None

    def __parseJobStatus__(self, xml):
        if xml.find("commandline") is not None:
            self.commandline = xml.find("commandline").text
        if xml.find("selfUri") is not None:
            self.jobUrl = xml.find("selfUri").find("url").text
        if xml.find("jobHandle") is not None:
            self.jobHandle = xml.find("jobHandle").text
        if xml.find("jobStage") is not None:
            self.jobStage = xml.find("jobStage").text
        if xml.find("terminalStage") is not None:
            self.terminalStage = (xml.find("terminalStage").text == "true")
        if xml.find("failed") is not None:
            self.failed = (xml.find("failed").text == "true")
            # self.metadata = 
        if xml.find("resultsUri") is not None:
            self.resultsUrl = xml.find("resultsUri").find("url").text
        if xml.find("workingDirUri") is not None:
            self.workingDirUrl = xml.find("workingDirUri").find("url").text
        if xml.find("dateSubmitted") is not None:
            self.dateSubmitted = xml.find("dateSubmitted").text
        # self.messages = [ m.find("text").text for elem in xml.find("messages") ] 
        if xml.find("messages") is not None:
            for m in xml.find("messages"):
                self.messages.append("%s: %s" % (m.find("timestamp").text, m.find("text").text))

    def show(self, messages=False):
        """ A debugging method to dump some of the content of this object to stdout """

        if not self.jobHandle and self.commandline:
            print("Submission validated.  Commandline is: '%s'" % (self.commandline))
            return

        str = "Job=%s" % (self.jobHandle)
        if self.terminalStage:
            if self.failed:
                str += ", failed at stage %s" % (self.jobStage)
            else:
                str += ", finished, results are at %s" % (self.resultsUrl)
        else:
            str += ", not finished, stage=%s" % (self.jobStage)
        print(str)
        if messages:
            for m in self.messages:
                print("\t%s" % (m))
            

    def update(self):
        r = self.client.__doGet__(url=self.jobUrl + "/?expand=true")
        self.__parseJobStatus__(ET.fromstring(r.text.encode('utf-8')))

    def delete(self):
        self.client.__doDelete__(url=self.jobUrl)

    def isDone(self):
        return self.terminalStage
        pass

    def isError(self):
        return self.failed
        pass

    def listResults(self, final=True):
        """Returns dictionary where key is filename and value is a ResultFile object.   If job isn't 
        finished yet and you want a list of what's in the job's working dir, use "final=False", though
        be aware that the working dir is transient and only exists once the job has been staged to the
        execution host and before it's been cleaned up."""  
        if final:
            url = self.resultsUrl
        else:
            url = self.workingDirUrl
        r = self.client.__doGet__(url=url)
        resultFiles = {}
        et = ET.fromstring(r.text.encode('utf-8'))
        for child in et.find("jobfiles"):
            resultFiles[child.find("filename").text] = ResultFile(self.client, child)
        return resultFiles

    def downloadResults(self, directory=None, final=True):
        """Downloads all result files to specified, existant directory, or current directory.  Set final=False
        if you want to download files from the working dir before the job has finished.  Once the job is finished
        use final=True to download the final results."""
        resultFiles = self.listResults(final=final)
        for filename in resultFiles: 
            resultFiles[filename].download(directory)

    def waitForCompletion(self, pollInterval=60):
        """ Wait for job to finish.  pollInterval is 60 seconds by default."""
        while not self.isDone():
            time.sleep(pollInterval)
            self.update()

class ResultFile(object): 
    def __init__(self, client, jobFileElement):
        self.client = client
        self.name = jobFileElement.find("filename").text
        self.url = jobFileElement.find("downloadUri").find("url").text 
        self.length = int(jobFileElement.find("length").text)

    def download(self, directory=None):
        if not directory:
            directory = os.getcwd()
        path = os.path.join(directory, self.name)

        if verbose:
            print("downloading from %s to %s" % (self.url, path))
        r = self.client.__doGet__(self.url, stream=True, isdownload=True)
        with open(path, 'wb') as outfile:
            shutil.copyfileobj(r.raw, outfile)
    
    def getName(self):
        return self.name

    def getLength(self):
        return self.length

    def getUrl(self):
        return self.url

class Application(object):
    
    def __init__(self):
        self.props = Props.Properties()
        confFile = "pycipres.conf"
        try:
            with open(confFile) as infile:
                self.props.load(infile)
        except IOError as e:
            raise
    
    """
    def __init__(self):
        found = False
        self.props = Props.Properties()
        confFile = os.path.expandvars(os.path.join("$SDK_VERSIONS", "testdata", "pycipres.conf"));
        found = True
        try:
            with open(confFile) as infile:
                self.props.load(infile)
        except IOError as e:
            pass

        confFile = os.path.join(os.path.expanduser("~"), "pycipres.conf");
        found = True
        try:
            with open(confFile) as infile:
                self.props.load(infile)
        except IOError as e:
            pass

        if not found:
            raise Exception("Didn't find pycipres.conf in $SDK_VERSIONS or in home directory.")
        requiredProperties = set(["APPNAME", "APPID", "USERNAME", "PASSWORD", "URL"])
        if not requiredProperties.issubset(self.props.propertyNames()):
            raise Exception("pycipres.conf doesn't contain all the required properties: %s" % ', '.join(requiredProperties))
        # if self.props.VERBOSE:
            # self.props.list()
        print("URL=%s" % (self.props.URL))
    """
    def getProperties(self):
        return self.props

#
#def main():
#    """
#        These are examples of how the class can be used.
#    """
#
#    global verbose
#    properties = Application().getProperties()
#    client = Client(properties.APPNAME, properties.APPID, properties.USERNAME, properties.PASSWORD, properties.URL)
#    if properties.VERBOSE:
#        verbose = True
#
#    try:
#
#        job = client.submitJob(
#            {"toolId" : "CLUSTALW", "runtime_" : ".1"},
#            {"infile_" : "/users/u4/terri/samplefiles/fasta/ex1.fasta"},
#            {"statusEmail" : "true"}, validateOnly=True)
#        job.show(messages=True)
#
#        """
#            If you want to submit a parameter where the pise type = List, and you want to send
#            multiple values for the parameter, instead of using a dictionary as the vParams argument
#            to submitJob, you must send a list of 2-tuples.  See "criteria_1_" below.
#
#            This functionality required an update to version 2.5.3 of the Requests library and
#            changes to the implementation of submitJob.
#        """
#        job = client.submitJob(
#            [
#                ("toolId", "JMODELTEST2_XSEDE"),
#                ("runtime_", "0.5"),
#                ("def_topsearch_", "NNI"),
#                ("criteria_1_", "-AIC"),
#                ("criteria_1_", "-DT"),
#                ("criteria_1_", "-AICc"),
#                ("criteria_1_", "-BIC"),
#                ("set_subschemes_", "203"),
#                ("uneq_basefmodels_", "0"),
#                ("invar_models_", "0"),
#                ("numratecat_models_", "8"),
#                ("parameter_importances_", "0"),
#                ("estimate_modelavg_", "0"),
#                ("print_paup_", "0")
#            ],
#            {"infile_" : "/users/u4/terri/samplefiles/fasta/ex1.fasta"},
#            {"statusEmail" : "true"}, validateOnly=True)
#        job.show(messages=True)
#        return 1
#
#    except ValidationError as ve:
#        print(ve.asString())
#        if verbose:
#            raise
#        return 1
#    except CipresError as ce:
#        print("CIPRES ERROR: %s" % ( ce ))
#        if verbose:
#            raise
#        return 1
#    except requests.exceptions.RequestException as e:
#        print("CONNECTION ERROR: %s" % (e))
#        if verbose:
#            raise 
#        return 1
#    except ET.ParseError as pe:
#        print("Unexpected response cannot be parsed.  Parsing error message: %s" % (pe))
#        if verbose:
#            raise
#        return 1
#
#
#
#if __name__ == "__main__":
#    sys.exit(main())
