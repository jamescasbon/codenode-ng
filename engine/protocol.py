

def parse_output(output):
    """Parse output and return the (cell type, cell output)

    Necessary to extract an image from surrounding text.  The tag 
    should enclose the data, i.e. 

       __celltype__
       Data...
       __celltype__
       
    #TODO: This will eventually produce a list of output types
    """
    
    cell_types = ['outputimage']
    default_cell_type = 'outputtext'

    for ctype in cell_types: 
        tag = '__%s__' % ctype
        if tag in output and output.count(tag) > 1: 
            # return the last possible chunk for the moment
            return (ctype, output.split(tag)[-2])
    
    return default_cell_type, output



def encode_image(data):
    """ create an encoded form of an image """
    coded = base64.b64encode(data)
    return "data:image/png;base64," + coded 
