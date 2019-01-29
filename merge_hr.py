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
        description='Merge HR data from Apple Watch GPX in Wahoo GPX')
    arg_parser.add_argument('wahoo_file', help='File Wahoo', type=str)
    arg_parser.add_argument('apple_file', help='File Wahoo', type=str)
    args = arg_parser.parse_args()

    if not args.wahoo_file:
        logger.error('Missing argument: Wahoo File')
        sys.exit()

    if not args.apple_file:
        logger.error('Missing argument: Apple File')
        sys.exit()

    if os.path.exists(args.wahoo_file):
        try:
            wahoo_gpx_file = open(args.wahoo_file, 'r')
            wahoo_gpx = gpxpy.parse(wahoo_gpx_file)
        except IOError: # whatever reader errors you care about
            logger.error('Cannot open Wahoo File')
            sys.exit()

    if os.path.exists(args.apple_file):
        try:
            apple_gpx_file = open(args.apple_file, 'r')
            apple_gpx = gpxpy.parse(apple_gpx_file)
        except IOError: # whatever reader errors you care about
            logger.error('Cannot open Apple File')
            sys.exit()
    
    hr = get_extension_hr(apple_gpx)

    for wahoo_track in wahoo_gpx.tracks:
        for wahoo_segment in wahoo_track.segments:
            for wahoo_point in wahoo_segment.points:
                if hr.get(wahoo_point.time,None) is not None:
                    wahoo_extensions = wahoo_point.extensions
                    if not wahoo_extensions:
                        pass

                    wahoo_extensions[0].append(hr[wahoo_point.time])

    print(wahoo_gpx.to_xml())

if __name__ == '__main__':
    main()