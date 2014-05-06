import os

from seishub_event_format_parser import readSeishubEventFile, NSMAP


def convert_and_validate(input_file, output_file):
    cat = readSeishubEventFile(input_file)
    try:
        cat.write(output_file, format="quakeml", validate=True, nsmap=NSMAP)
    except:
        output_file = "/tmp/%s" % os.path.basename(output_file)
        cat.write(output_file, format="quakeml", validate=False, nsmap=NSMAP)
        msg = "Validation failed. See file: %s" % output_file
        raise Exception(msg)


if __name__ == "__main__":
    all_files = os.listdir("./all_resources")
    for _i, filename in enumerate(all_files):
        filename = os.path.join("./all_resources", filename)
        output_name = os.path.join("./converted_files",
            os.path.basename(filename))
        if not output_name.endswith(".xml"):
            output_name += ".xml"
        if os.path.exists(output_name):
            continue
        print "Converting file %s (%i of %i)" % (filename, _i + 1,
            len(all_files))
        convert_and_validate(filename, output_name)
