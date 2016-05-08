""" Core exceptions raised by the ONVIF Client """

from suds import WebFault, MethodNotFound, PortNotFound, \
        ServiceNotFound, TypeNotFound, BuildError

# Error codes setting
# Error unknown, e.g, HTTP errors
ERR_ONVIF_UNKNOWN = 1
# Protocol error returned by WebService,
# e.g:DataEncodingUnknown, MissingAttr, InvalidArgs, ...
ERR_ONVIF_PROTOCOL = 2
# Error about WSDL instance
ERR_ONVIF_WSDL     = 3
# Error about Build
ERR_ONVIF_BUILD    = 4


class SoapHeadersNotPermitted(Exception):
    msg = """
        Method (%s) was invoked with SOAP headers. The WSDL does not define
        SOAP headers for this method. Retry without the soapheaders keyword
        argument.
        """
    def __init__(self, name):
            Exception.__init__(self, self.msg % name)

class ONVIFError(Exception):
    def __init__(self, err):
        if isinstance(err, (WebFault, SoapHeadersNotPermitted)):
            self.reason = err.fault.Reason.Text
            self.fault = err.fault
            self.code = ERR_ONVIF_PROTOCOL
        elif isinstance(err, (ServiceNotFound, PortNotFound,
                              MethodNotFound, TypeNotFound)):
            self.reason = str(err)
            self.code = ERR_ONVIF_PROTOCOL
        elif isinstance(err, BuildError):
            self.reason = str(err)
            self.code = ERR_ONVIF_BUILD
        else:
            self.reason = 'Unknown error: ' + str(err)
            self.code = ERR_ONVIF_UNKNOWN

    def __str__(self):
        return self.reason
