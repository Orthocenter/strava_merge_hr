import gpxpy
import gpxpy.gpx
import argparse
import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_extension_hr(gpxpy_instance):
    """
    return a dict with all extension values from all track points.
    """
    hr = {}

    for track in gpxpy_instance.tracks:
        for segment in track.segments:
            for point in segment.points:
                extensions = point.extensions
                if not extensions:
                    return None

                for child in extensions[0].getchildren():
                    tag = child.tag.rsplit("}", 1)[-1] # FIXME

                    if tag == 'hr':
                        hr[point.time] = child

    return hr

def main():
    arg_parser = argparse.ArgumentParser(
        description='Merge HR data from Apple Watch Watch GPX in iPhone GPX')
    arg_parser.add_argument('--iphone_file', help='File iPhone', type=str)
    arg_parser.add_argument('--watch_file', help='File Watch', type=str)
    args = arg_parser.parse_args()

    if not args.iphone_file:
        logger.error('Missing argument: iPhone File')
        sys.exit()

    if not args.watch_file:
        logger.error('Missing argument: Apple Watch File')
        sys.exit()

    if os.path.exists(args.iphone_file):
        try:
            iphone_gpx_file = open(args.iphone_file, 'r')
            iphone_gpx = gpxpy.parse(iphone_gpx_file)
        except IOError: # whatever reader errors you care about
            logger.error('Cannot open iPhone File')
            sys.exit()

    if os.path.exists(args.watch_file):
        try:
            watch_gpx_file = open(args.watch_file, 'r')
            watch_gpx = gpxpy.parse(watch_gpx_file)
        except IOError: # whatever reader errors you care about
            logger.error('Cannot open Apple Watch File')
            sys.exit()
    
    hr = get_extension_hr(watch_gpx)

    for iphone_track in iphone_gpx.tracks:
        for iphone_segment in iphone_track.segments:
            for iphone_point in iphone_segment.points:
                if hr.get(iphone_point.time,None) is not None:
                    iphone_extensions = iphone_point.extensions
                    if not iphone_extensions:
                        pass

                    iphone_extensions[0].append(hr[iphone_point.time])

    print(iphone_gpx.to_xml())

if __name__ == '__main__':
    main()