from obspy.core.event import validate
import os

from seishub_event_format_parser import readSeishubEventFile


def convert_and_validate(input_file, output_file):
    cat = readSeishubEventFile(input_file)
    cat.write(output_file, format="quakeml")

    ver = validate(output_file)
    if ver is True:
        return
    else:
        raise Exception


if __name__ == "__main__":
    all_files = os.listdir("./all_resources")
    for _i, filename in enumerate(all_files):
        filename = os.path.join("./all_resources", filename)
        output_name = os.path.join("./converted_files",
            os.path.basename(filename))
        if os.path.exists(output_name):
            continue
        print "Converting file %s (%i of %i)" % (filename, _i + 1,
            len(all_files))
        convert_and_validate(filename, output_name)