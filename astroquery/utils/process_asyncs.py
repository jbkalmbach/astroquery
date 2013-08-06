# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Process all "async" methods into direct methods.
"""

from class_or_instance import class_or_instance
import textwrap

def process_asyncs(cls):
    """
    Convert all query_x_async methods to query_x methods

    (see
    http://stackoverflow.com/questions/18048341/add-methods-to-a-class-generated-from-other-methods
    for help understanding)
    """
    
    def create_method(async_method):

        @class_or_instance
        def newmethod(self, *args, **kwargs):
            if 'verbose' in kwargs:
                verbose = kwargs.pop('verbose')
            else:
                verbose = False
            response = async_method(*args,**kwargs)
            result = self._parse_result(response, verbose=verbose)
            return result

        return newmethod

    methods = cls.__dict__.keys()

    for k in methods:
        newmethodname = k.replace("_async","")
        if 'async' in k and newmethodname not in methods:

            async_method = getattr(cls,k)

            newmethod = create_method(async_method)

            newmethod.fn.__doc__ = async_to_sync_docstr(async_method.__doc__)

            setattr(cls,newmethodname,newmethod)

    return cls

def async_to_sync_docstr(doc, returntype='table'):
    """
    Strip of the "Returns" component of a docstr and replace it with "Returns a
    table" code
    """

    object_dict = {'table':'astropy.table.Table',
                   'fits':'astropy.io.fits.PrimaryHDU'}

    firstline = "Queries the service and returns a {rt} object".format(rt=returntype)

    returnstr = """
                Returns
                -------
                A `{ot}` object
                """.format(ot=object_dict[returntype])

    lines = doc.split('\n')
    outlines = []
    rblock = False
    for line in lines:
        lstrip = line.strip()
        if lstrip == "Returns":
            rblock = True
            continue
        if rblock:
            if lstrip == '':
                rblock = False
                continue
            else:
                continue
        outlines.append(lstrip)

    newdoc = "\n".join([firstline] + lines + [textwrap.dedent(returnstr)])

    return newdoc
