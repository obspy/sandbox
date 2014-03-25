#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Seishub event file format converter.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), Tobias Megies, 2012

:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from obspy.core import UTCDateTime, AttribDict
from obspy.core.event import Catalog, Event, Origin, \
    Magnitude, StationMagnitude, Comment, Pick, WaveformStreamID, \
    OriginQuality, Arrival, FocalMechanism, NodalPlanes, NodalPlane, \
    StationMagnitudeContribution, OriginUncertainty
from obspy.core.util.xmlwrapper import XMLParser
from obspy.core.util import kilometer2degrees
import os
import math

NOW = UTCDateTime()

def fix_station_name(station):
    return station.rstrip("_")


RESOURCE_ROOT = "smi:de.erdbeben-in-bayern"

NAMESPACE = ("edb", "http://erdbeben-in-bayern.de/xmlns/0.1")

STATION_DICT = {
    "MUN1": "UH2",
    "MUN2": "UH1",
}

CURRENT_TYPE = None

NETWORK_DICT = {
    # XXX: Custom mappings as no SEED file available.
    "BERN": "XX",
    "VACK": "XX",
    "JIND": "XX",
    "LUBY": "XX",
    "POCA": "XX",
    "STAU": "BW",
    "SCE1": "BW",
    "GRC4": "GR",
    "GRC3": "GR",
    "GRB1": "GR",
    "GRB2": "GR",
    "GRB3": "GR",
    "GRB4": "GR",
    "GRB5": "GR",
    "SWM2": "BW",
    "LAC":  "XX",
    "KOC": "XX",
    "ARSA": "OE",
    "OBKA": "OE",
    "MOX": "GR",
    "GRA1": "GR",
    "GRA3": "GR",
    "GRC2": "GR",
    "STO": "XX",
    "PUE": "XX",
    "P10": "XX",
    "P09": "XX",
    "NOT": "XX",
    "NAB": "XX",
    "MIT": "XX",
    "EIK": "XX",
    "BER": "XX",
    "HBR": "XX",
    "CHKA": "XX",
    "GRA4": "GR",
    "GRA2": "GR",
    "BCHKA": "XX",
    "TNS": "GR",

    # Known mappings.
    "ALTM": "BW",
    "BE1": "BW",
    "BE2": "BW",
    "BE3": "BW",
    "BE4": "BW",
    "BGLD": "BW",
    "BW01": "BW",
    "DHFO": "BW",
    "FURT": "BW",
    "HROE": "BW",
    "KW1": "BW",
    "KW2": "BW",
    "KW3": "BW",
    "KW4": "BW",
    "MANZ": "BW",
    "MASC": "BW",
    "MGBB": "BW",
    "MHAI": "BW",
    "MKON": "BW",
    "MROB": "BW",
    "MSBB": "BW",
    "MZEK": "BW",
    "NORI": "BW",
    "NZC2": "BW",
    "NZG0": "BW",
    "OBER": "BW",
    "OBHA": "BW",
    "PART": "BW",
    "RJOB": "BW",
    "RLAS": "BW",
    "RMOA": "BW",
    "RNHA": "BW",
    "RNON": "BW",
    "ROTZ": "BW",
    "RTAK": "BW",
    "RTBE": "BW",
    "RTBM": "BW",
    "RTSA": "BW",
    "RTSH": "BW",
    "RTFS": "BW",
    "RTVS": "BW",
    "RWMO": "BW",
    "UH1": "BW",
    "UH2": "BW",
    "UH3": "BW",
    "UH4": "BW",
    "UHE": "BW",
    "VIEL": "BW",
    "WETR": "BW",
    "ZUGS": "BW",
    "NKC": "CZ",
    "FUR": "GR",
    "GEC2": "GR",
    "GRC1": "GR",
    "WET": "GR",
    "CRLZ": "NZ",
    "DAVA": "OE",
    "MOA": "OE",
    "MOTA": "OE",
    "RETA": "OE",
    "WATA": "OE",
    "WTTA": "OE",
}

NETWORK_DICT.update(
{'ALTM': 'BW',
 'BE1': 'BW',
 'BE2': 'BW',
 'BE3': 'BW',
 'BE4': 'BW',
 'BGLD': 'BW',
 'DAVA': 'OE',
 'DHFO': 'BW',
 'FETA': 'OE',
 'FUR': 'GR',
 'FURT': 'BW',
 'GEC2': 'GR',
 'GRC1': 'GR',
 'HROE': 'BW',
 'KBA': 'OE',
 'KW1': 'BW',
 'KW2': 'BW',
 'KW3': 'BW',
 'KW4': 'BW',
 'MANZ': 'BW',
 'MASC': 'BW',
 'MGBB': 'BW',
 'MHAI': 'BW',
 'MKON': 'BW',
 'MOA': 'OE',
 'MOTA': 'OE',
 'MROB': 'BW',
 'MSBB': 'BW',
 'MZEK': 'BW',
 'NKC': 'CZ',
 'NORI': 'BW',
 'NZC2': 'BW',
 'NZG0': 'BW',
 'OBER': 'BW',
 'PART': 'BW',
 'RETA': 'OE',
 'RHAM': 'BW',
 'RJOB': 'BW',
 'RLAS': 'BW',
 'RMOA': 'BW',
 'RNHA': 'BW',
 'RNON': 'BW',
 'ROTZ': 'BW',
 'RTAK': 'BW',
 'RTBE': 'BW',
 'RTBM': 'BW',
 'RTEA': 'BW',
 'RTFA': 'BW',
 'RTKA': 'BW',
 'RTLI': 'BW',
 'RTPA': 'BW',
 'RTPI': 'BW',
 'RTSA': 'BW',
 'RTSH': 'BW',
 'RTSL': 'BW',
 'RTSP': 'BW',
 'RTSW': 'BW',
 'RTVS': 'BW',
 'RTZA': 'BW',
 'RWMO': 'BW',
 'SCE': 'BW',
 'SQTA': 'OE',
 'UH1': 'BW',
 'UH2': 'BW',
 'UH3': 'BW',
 'UH4': 'BW',
 'UHE': 'BW',
 'UHK': 'BW',
 'UHL': 'BW',
 'VIEL': 'BW',
 'WERN': 'SX',
 'WET': 'GR',
 'WETR': 'BW',
 'WTTA': 'OE',
 'ZUGS': 'BW'})


def isSeishubEventFile(filename):
    """
    Checks whether a file is a Seishub Event file.

    This is a very rough test as the format is not very well defined and has no
    unique features.

    :type filename: str
    :param filename: Name of the Seishub event file to be checked.
    :rtype: bool
    :return: ``True`` if Seishub event file.

    .. rubric:: Example
    """
    try:
        parser = XMLParser(filename)
    except:
        return False
    # Simply check to paths that should always exist.
    if parser.xpath('event_id/value') and parser.xpath('event_type/value'):
        return True
    return False


def __toValueQuantity(parser, element, name, quantity_type=None):
    try:
        el = parser.xpath(name, element)[0]
    except:
        return None, None

    value = parser.xpath2obj('value', el, quantity_type)
    errors = {}
    error_types = ["uncertainty", "lowerUncertainty", "upperUncertainty",
        "confidenceLevel"]
    for er_type in error_types:
        error = parser.xpath2obj(er_type, el, float)
        if error:
            errors[er_type.replace("U", "_u")] = error
        error = parser.xpath2obj(er_type, el, float)
    return value, errors


def __toFloatQuantity(parser, element, name):
    return __toValueQuantity(parser, element, name, float)


def __toTimeQuantity(parser, element, name):
    return __toValueQuantity(parser, element, name, UTCDateTime)


def __toOrigin(parser, origin_el, public_id):
    """
    Parses a given origin etree element.

    :type parser: :class:`~obspy.core.util.xmlwrapper.XMLParser`
    :param parser: Open XMLParser object.
    :type origin_el: etree.element
    :param origin_el: origin element to be parsed.
    :return: A ObsPy :class:`~obspy.core.event.Origin` object.
    """
    global CURRENT_TYPE

    origin = Origin()
    origin.resource_id = "/".join([RESOURCE_ROOT, "origin", public_id, "1"])

    # I guess setting the program used as the method id is fine.
    origin.method_id = "%s/location_method/%s" % (RESOURCE_ROOT,
        parser.xpath2obj('program', origin_el))
    if str(origin.method_id).lower().endswith("none"):
        origin.method_id = None

    # Standard parameters.
    origin.time, origin.time_errors = \
        __toTimeQuantity(parser, origin_el, "time")
    origin.latitude, origin_latitude_error = \
        __toFloatQuantity(parser, origin_el, "latitude")
    origin.longitude, origin_longitude_error = \
        __toFloatQuantity(parser, origin_el, "longitude")
    origin.depth, origin.depth_errors = \
        __toFloatQuantity(parser, origin_el, "depth")

    if origin_longitude_error:
        origin_longitude_error = origin_longitude_error["uncertainty"]
    if origin_latitude_error:
        origin_latitude_error = origin_latitude_error["uncertainty"]

    # Figure out the depth type.
    depth_type = parser.xpath2obj("depth_type", origin_el)

    # Map Seishub specific depth type to the QuakeML depth type.
    if depth_type == "from location program":
        depth_type = "from location"
    if depth_type is not None:
        origin.depth_type = depth_type

    # XXX: CHECK DEPTH ORIENTATION!!

    if CURRENT_TYPE == "seiscomp3":
        origin.depth *= 1000
        if origin.depth_errors.uncertainty:
            origin.depth_errors.uncertainty *= 1000
    else:
        # Convert to m.
        origin.depth *= -1000
        if origin.depth_errors.uncertainty:
            origin.depth_errors.uncertainty *= 1000

    # Earth model.
    earth_mod = parser.xpath2obj('earth_mod', origin_el, str)
    if earth_mod:
        earth_mod = earth_mod.split()
        earth_mod = ",".join(earth_mod)
        origin.earth_model_id = "%s/earth_model/%s" % (RESOURCE_ROOT,
            earth_mod)

    if (origin_latitude_error is None or origin_longitude_error is None) and \
        CURRENT_TYPE not in ["seiscomp3", "toni"]:
        print "AAAAAAAAAAAAA"
        raise Exception

    if origin_latitude_error and origin_latitude_error:
        if CURRENT_TYPE in ["baynet", "obspyck"]:
            uncert = OriginUncertainty()
            if origin_latitude_error > origin_longitude_error:
                uncert.azimuth_max_horizontal_uncertainty = 0
            else:
                uncert.azimuth_max_horizontal_uncertainty = 90
            uncert.min_horizontal_uncertainty, \
                uncert.max_horizontal_uncertainty = \
                sorted([origin_longitude_error, origin_latitude_error])
            uncert.min_horizontal_uncertainty *= 1000.0
            uncert.max_horizontal_uncertainty *= 1000.0
            uncert.preferred_description = "uncertainty ellipse"
            origin.origin_uncertainty = uncert
        elif CURRENT_TYPE == "earthworm":
            uncert = OriginUncertainty()
            uncert.horizontal_uncertainty = origin_latitude_error
            uncert.horizontal_uncertainty *= 1000.0
            uncert.preferred_description = "horizontal uncertainty"
            origin.origin_uncertainty = uncert
        elif CURRENT_TYPE in ["seiscomp3", "toni"]:
            pass
        else:
            raise Exception

    # Parse the OriginQuality if applicable.
    if not origin_el.xpath("originQuality"):
        return origin

    origin_quality_el = origin_el.xpath("originQuality")[0]
    origin.quality = OriginQuality()
    origin.quality.associated_phase_count = \
        parser.xpath2obj("associatedPhaseCount", origin_quality_el, int)
    # QuakeML does apparently not distinguish between P and S wave phase
    # count. Some Seishub event files do.
    p_phase_count = parser.xpath2obj("P_usedPhaseCount", origin_quality_el,
                                     int)
    s_phase_count = parser.xpath2obj("S_usedPhaseCount", origin_quality_el,
                                     int)
    # Use both in case they are set.
    if p_phase_count and s_phase_count:
        phase_count = p_phase_count + s_phase_count
        # Also add two Seishub element file specific elements.
        origin.quality.p_used_phase_count = p_phase_count
        origin.quality.s_used_phase_count = s_phase_count
    # Otherwise the total usedPhaseCount should be specified.
    else:
        phase_count = parser.xpath2obj("usedPhaseCount",
                                       origin_quality_el, int)
    origin.quality.used_phase_count = phase_count

    associated_station_count = \
        parser.xpath2obj("associatedStationCount", origin_quality_el, int)
    used_station_count = parser.xpath2obj("usedStationCount",
        origin_quality_el, int)
    depth_phase_count = parser.xpath2obj("depthPhaseCount", origin_quality_el,
        int)
    standard_error = parser.xpath2obj("standardError", origin_quality_el,
        float)
    azimuthal_gap = parser.xpath2obj("azimuthalGap", origin_quality_el, float)
    secondary_azimuthal_gap = \
        parser.xpath2obj("secondaryAzimuthalGap", origin_quality_el, float)
    ground_truth_level = parser.xpath2obj("groundTruthLevel",
        origin_quality_el, str)
    minimum_distance = parser.xpath2obj("minimumDistance", origin_quality_el,
        float)
    maximum_distance = parser.xpath2obj("maximumDistance", origin_quality_el,
        float)
    median_distance = parser.xpath2obj("medianDistance", origin_quality_el,
        float)
    if minimum_distance is not None:
        minimum_distance = kilometer2degrees(minimum_distance)
    if maximum_distance is not None:
        maximum_distance = kilometer2degrees(maximum_distance)
    if median_distance is not None:
        median_distance = kilometer2degrees(median_distance)

    if associated_station_count is not None:
        origin.quality.associated_station_count = associated_station_count
    if used_station_count is not None:
        origin.quality.used_station_count = used_station_count
    if depth_phase_count is not None:
        origin.quality.depth_phase_count = depth_phase_count
    if standard_error is not None and not math.isnan(standard_error):
        origin.quality.standard_error = standard_error
    if azimuthal_gap is not None:
        origin.quality.azimuthal_gap = azimuthal_gap
    if secondary_azimuthal_gap is not None:
        origin.quality.secondary_azimuthal_gap = secondary_azimuthal_gap
    if ground_truth_level is not None:
        origin.quality.ground_truth_level = ground_truth_level
    if minimum_distance is not None:
        origin.quality.minimum_distance = minimum_distance
    if maximum_distance is not None:
        origin.quality.maximum_distance = maximum_distance
    if median_distance is not None and not math.isnan(median_distance):
        origin.quality.median_distance = median_distance

    return origin


def __toMagnitude(parser, magnitude_el, public_id):
    """
    Parses a given magnitude etree element.

    :type parser: :class:`~obspy.core.util.xmlwrapper.XMLParser`
    :param parser: Open XMLParser object.
    :type magnitude_el: etree.element
    :param magnitude_el: magnitude element to be parsed.
    :return: A ObsPy :class:`~obspy.core.event.Magnitude` object.
    """
    global CURRENT_TYPE
    mag = Magnitude()
    mag.resource_id = "/".join([RESOURCE_ROOT, "magnitude", public_id, "1"])
    mag.mag, mag.mag_errors = __toFloatQuantity(parser, magnitude_el, "mag")
    # obspyck used to write variance (instead of std) in magnitude error fields
    if CURRENT_TYPE == "obspyck":
        if mag.mag_errors.uncertainty is not None:
            mag.mag_errors.uncertainty = math.sqrt(mag.mag_errors.uncertainty)
    mag.magnitude_type = parser.xpath2obj("type", magnitude_el)
    mag.station_count = parser.xpath2obj("stationCount", magnitude_el, int)
    mag.method_id = "%s/magnitude_method/%s" % (RESOURCE_ROOT,
        parser.xpath2obj('program', magnitude_el))
    if str(mag.method_id).lower().endswith("none"):
        mag.method_id = None

    return mag


def __toStationMagnitude(parser, stat_mag_el, public_id, stat_mag_count):
    """
    Parses a given station magnitude etree element.

    :type parser: :class:`~obspy.core.util.xmlwrapper.XMLParser`
    :param parser: Open XMLParser object.
    :type stat_mag_el: etree.element
    :param stat_mag_el: station magnitude element to be parsed.
    return: A ObsPy :class:`~obspy.core.event.StationMagnitude` object.
    """
    global CURRENT_TYPE
    mag = StationMagnitude()
    mag.mag, mag.mag_errors = __toFloatQuantity(parser, stat_mag_el, "mag")
    mag.resource_id = "/".join([RESOURCE_ROOT, "station_magnitude", public_id, str(stat_mag_count)])
    # Use the waveform id to store station and channel(s) in the form
    # station.[channel_1, channel_2] or station.channel in the case only one
    # channel has been used.
    # XXX: This might be a violation of how this field is used within QuakeML
    channels = parser.xpath2obj('channels', stat_mag_el).split(',')
    channels = ','.join([_i.strip() for _i in channels])
    if len(channels) > 1:
        channels = '%s' % channels
    station = fix_station_name(parser.xpath2obj('station', stat_mag_el))
    location = parser.xpath2obj('location', stat_mag_el, str) or ""
    mag.waveform_id = WaveformStreamID()
    # Map some station names.
    if station in STATION_DICT:
        station = STATION_DICT[station]
    mag.waveform_id.station_code = station

    network = parser.xpath2obj('network', stat_mag_el)
    if network is None:
        # network id is not stored in original stationMagnitude, try to find it
        # in a pick with same station name
        for waveform in parser.xpath("pick/waveform"):
            if waveform.attrib.get("stationCode") == station:
                network = waveform.attrib.get("networkCode")
                break
    if network is None:
        network = NETWORK_DICT[station]
    if network is None:
        print "AAAAAAAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHH"
        raise Exception

    if "," not in channels:
        mag.waveform_id.channel_code = channels
    mag.waveform_id.network_code = network
    mag.waveform_id.location_code = location
    return mag


def __toFocalMechanism(parser, focmec_el, public_id, focmec_number):
    """
    """
    global CURRENT_TYPE
    focmec = FocalMechanism()
    focmec.resource_id = "/".join([RESOURCE_ROOT, "focal_mechanism", public_id, str(focmec_number)])
    focmec.method_id = "%s/focal_mechanism_method/%s" % (RESOURCE_ROOT,
        parser.xpath2obj('program', focmec_el))
    if str(focmec.method_id).lower().endswith("none"):
        focmec.method_id = None
    focmec.station_polarity_count = parser.xpath2obj("stationPolarityCount",
        focmec_el, int)
    if focmec.station_polarity_count:
        focmec.misfit = parser.xpath2obj("stationPolarityErrorCount",
                focmec_el, int) / float(focmec.station_polarity_count)
    focmec.nodal_planes = NodalPlanes()
    focmec.nodal_planes.nodal_plane_1 = NodalPlane()
    nodal_plane = focmec_el.find("nodalPlanes")
    if nodal_plane is None or not len(nodal_plane):
        return None
    n_p = focmec.nodal_planes.nodal_plane_1
    # There is always only one nodal plane, called nodalPlane1
    n_p.strike, strike_uncertainty = __toFloatQuantity(parser,
        focmec_el, "nodalPlanes/nodalPlane1/strike")
    n_p.dip, dip_uncertainty = __toFloatQuantity(parser, focmec_el,
        "nodalPlanes/nodalPlane1/dip")
    n_p.rake, rake_uncertainty = __toFloatQuantity(parser,
        focmec_el, "nodalPlanes/nodalPlane1/rake")
    if hasattr(strike_uncertainty, "uncertainty"):
        n_p.strike_errors.uncertainty = strike_uncertainty["uncertainty"]
    if hasattr(dip_uncertainty, "uncertainty"):
        n_p.dip_errors.uncertainty = dip_uncertainty["uncertainty"]
    if hasattr(rake_uncertainty, "uncertainty"):
        n_p.rake_errors.uncertainty = rake_uncertainty["uncertainty"]
    solution_count = parser.xpath2obj("possibleSolutionCount", focmec_el, int)
    if solution_count:
        focmec.comments.append(Comment("Possible Solution Count: %i" %
            solution_count))
    return focmec


def __toPick(parser, pick_el, evaluation_mode, public_id, pick_number):
    """
    """
    pick = Pick()
    pick.resource_id = "/".join([RESOURCE_ROOT, "pick", public_id, str(pick_number)])

    # Raise a warnings if there is a phase delay
    phase_delay = parser.xpath2obj("phase_delay", pick_el, float)
    if phase_delay is not None:
        msg = "The pick has a phase_delay!"
        raise Exception(msg)

    waveform = pick_el.xpath("waveform")[0]
    network = waveform.get("networkCode")
    station = fix_station_name(waveform.get("stationCode"))
    # Map some station names.
    if station in STATION_DICT:
        station = STATION_DICT[station]
    if not network:
        network = NETWORK_DICT[station]

    location = waveform.get("locationCode") or ""
    channel = waveform.get("channelCode") or ""
    pick.waveform_id = WaveformStreamID(
                                network_code=network,
                                station_code=station,
                                channel_code=channel,
                                location_code=location)
    pick.time, pick.time_errors = __toTimeQuantity(parser, pick_el, "time")
    # Picks without time are not quakeml conform
    if pick.time is None:
        print "Pick has no time and is ignored: %s %s" % (public_id, station)
        return None
    pick.phase_hint = parser.xpath2obj('phaseHint', pick_el, str)
    onset = parser.xpath2obj('onset', pick_el)
    # Fixing bad and old typo ...
    if onset == "implusive":
        onset = "impulsive"
    if onset:
        pick.onset = onset.lower()
    # Evaluation mode of a pick is global in the SeisHub Event file format.
    #pick.evaluation_mode = evaluation_mode
    # The polarity needs to be mapped.
    polarity = parser.xpath2obj('polarity', pick_el)
    pol_map_dict = {'up': 'positive', 'positive': 'positive',
                    'forward': 'positive',
                    'forwards': 'positive',
                    'right': 'positive',
                    'backward': 'negative',
                    'backwards': 'negative',
                    'left': 'negative',
                    'down': 'negative', 'negative': 'negative',
                    'undecidable': 'undecidable',
                    'poorup': 'positive',
                    'poordown': 'negative'}
    if polarity:
        if polarity.lower() in pol_map_dict:
            pick.polarity = pol_map_dict[polarity.lower()]
        else:
            pick.polarity = polarity.lower()

    pick_weight = parser.xpath2obj('weight', pick_el, int)
    if pick_weight is not None:
        pick.extra = AttribDict()
        pick.extra.weight = {'value': pick_weight, '_namespace': NAMESPACE}
    return pick


def __toArrival(parser, pick_el, evaluation_mode, public_id, pick_number):
    """
    """
    global CURRENT_TYPE
    arrival = Arrival()
    arrival.resource_id = "/".join([RESOURCE_ROOT, "arrival", public_id, str(pick_number)])
    arrival.pick_id = "/".join([RESOURCE_ROOT, "pick", public_id, str(pick_number)])
    arrival.phase = parser.xpath2obj('phaseHint', pick_el)
    arrival.azimuth = parser.xpath2obj('azimuth/value', pick_el, float)
    arrival.distance = parser.xpath2obj('epi_dist/value', pick_el, float)
    if arrival.distance is not None:
        arrival.distance = kilometer2degrees(arrival.distance)
    takeoff_angle, _ = __toFloatQuantity(parser, pick_el, "incident/value")
    if takeoff_angle and not math.isnan(takeoff_angle):
        arrival.takeoff_angle = takeoff_angle
    arrival.time_residual = parser.xpath2obj('phase_res/value', pick_el, float)
    arrival.time_weight = parser.xpath2obj('phase_weight/value', pick_el, float)
    return arrival


def readSeishubEventFile(filename):
    """
    Reads a Seishub event file and returns a ObsPy Catalog object.

    .. warning::
        This function should NOT be called directly, it registers via the
        ObsPy :func:`~obspy.core.event.readEvents` function, call this instead.

    :type filename: str
    :param filename: Seishub event file to be read.
    :rtype: :class:`~obspy.core.event.Catalog`
    :return: A ObsPy Catalog object.

    .. rubric:: Example
    """
    global CURRENT_TYPE

    base_name = os.path.basename(filename)

    if base_name.lower().startswith("baynet"):
        CURRENT_TYPE = "baynet"
    elif base_name.lower().startswith("earthworm"):
        CURRENT_TYPE = "earthworm"
    elif base_name.lower().startswith("gof"):
        CURRENT_TYPE = "seiscomp3"
    elif base_name.lower().startswith("obspyck") or base_name == "5622":
        CURRENT_TYPE = "obspyck"
    elif base_name.lower().startswith("toni"):
        CURRENT_TYPE = "toni"
    else:
        print "AAAAAAAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHH"
        raise Exception

    # Just init the parser, the SeisHub event file format has no namespaces.
    parser = XMLParser(filename)
    # Create new Event object.
    public_id = parser.xpath('event_id/value')[0].text

    # A Seishub event just specifies a single event so Catalog information is
    # not really given.
    catalog = Catalog()
    catalog.resource_id = "/".join([RESOURCE_ROOT, "catalog", public_id])

    # Read the event_type tag.
    account = parser.xpath2obj('event_type/account', parser, str)
    user = parser.xpath2obj('event_type/user', parser, str)
    global_evaluation_mode = parser.xpath2obj('event_type/value', parser, str)
    public = bool(parser.xpath2obj('event_type/public', parser, str))
    if account is not None and account.lower() != "sysop":
        public = False
    # The author will be stored in the CreationInfo object. This will be the
    # creation info of the event as well as on all picks.
    author = user
    if CURRENT_TYPE in ["seiscomp3", "earthworm"]:
        author = CURRENT_TYPE
    creation_info = {"author": author,
        "agency_id": "Erdbebendienst Bayern",
        "agency_uri": "%s/agency" % RESOURCE_ROOT,
        "creation_time": NOW}

    # Create the event object.
    event = Event(resource_id="/".join([RESOURCE_ROOT, "event", public_id, "1"]),
        creation_info=creation_info)
    # If account is None or 'sysop' and public is true, write 'public in the
    # comment, 'private' otherwise.
    event.extra = AttribDict()
    event.extra.public = {'value': public, '_namespace': NAMESPACE}
    event.extra.evaluationMode = {'value': global_evaluation_mode, '_namespace': NAMESPACE}

    event_type = parser.xpath2obj('type', parser, str)
    if event_type is not None:
        if event_type == "induced earthquake":
            event_type = "induced or triggered event"
        if event_type != "null":
            event.event_type = event_type

    # Parse the origins.
    origins = parser.xpath("origin")
    if len(origins) > 1:
        msg = "Only files with a single origin are currently supported"
        raise Exception(msg)
    for origin_el in parser.xpath("origin"):
        origin = __toOrigin(parser, origin_el, public_id)
        event.origins.append(origin)
    # Parse the magnitudes.
    for magnitude_el in parser.xpath("magnitude"):
        magnitude = __toMagnitude(parser, magnitude_el, public_id)
        if magnitude.mag is None:
            continue
        event.magnitudes.append(magnitude)
    # Parse the picks. Pass the global evaluation mode (automatic, manual)
    for _i, pick_el in enumerate(parser.xpath("pick")):
        pick = __toPick(parser, pick_el, global_evaluation_mode, public_id,
                   _i + 1)
        if pick is None:
            continue
        event.picks.append(pick)
    # The arrival object gets the following things from the Seishub.pick
    # objects
    # arrival.time_weight = pick.phase_weight
    # arrival.time_residual = pick.phase_res
    # arrival.azimuth = pick.azimuth
    # arrival.take_off_angle = pick.incident
    # arrival.distance = hyp_dist
    for _i, pick_el in enumerate(parser.xpath("pick")):
        arrival = __toArrival(parser, pick_el, global_evaluation_mode,
                public_id, _i + 1)
        if event.origins:
            event.origins[0].arrivals.append(arrival)

    for mag in event.station_magnitudes:
        mag.origin_id = event.origins[0].resource_id

    # Parse the station magnitudes.
    for _i, stat_magnitude_el in enumerate(parser.xpath("stationMagnitude")):
        stat_magnitude = __toStationMagnitude(parser, stat_magnitude_el,
            public_id, _i + 1)
        event.station_magnitudes.append(stat_magnitude)

    for mag in event.station_magnitudes:
        mag.origin_id = event.origins[0].resource_id

    for _i, stat_mag in enumerate(event.station_magnitudes):
        contrib = StationMagnitudeContribution()
        weight = None
        # The order of station magnitude objects is the same as in the xml
        # file.
        weight = parser.xpath2obj("weight",
            parser.xpath("stationMagnitude")[_i], float)
        if weight is not None:
            contrib.weight = weight
        contrib.station_magnitude_id = stat_mag.resource_id
        event.magnitudes[0].station_magnitude_contributions.append(contrib)

    for _i, foc_mec_el in enumerate(parser.xpath("focalMechanism")):
        foc_mec = __toFocalMechanism(parser, foc_mec_el, public_id, _i + 1)
        if foc_mec is not None:
            event.focal_mechanisms.append(foc_mec)

    # Set the origin id for the focal mechanisms. There is only one origin per
    # SeisHub event file.
    for focmec in event.focal_mechanisms:
        focmec.triggering_origin_id = event.origins[0].resource_id

    # Add the event to the catalog
    catalog.append(event)

    return catalog
