'''
Copyright (c) 2017 VMware, Inc. All Rights Reserved.
SPDX-License-Identifier: BSD-2-Clause
'''

import command_lib.command_lib
from report import formats

'''
Functions to generate content for the report
'''


def print_invoke_list(info_dict, info):
    '''Print out the list of command snippets that get invoked to retrive
    package information.
    info_dict: get_base_listing or get_command_listing from
    command_lib/command_lib.py
    info: the required key (niames, versions, licenses, etc)'''
    report = ''
    if 'invoke' in info_dict[info]:
        report = report + info + ':\n'
        for step in range(1, len(info_dict[info]['invoke'].keys()) + 1):
            if 'container' in info_dict[info]['invoke'][step]:
                report = report + formats.invoke_in_container
                for snippet in info_dict[info]['invoke'][step]['container']:
                    report = report + '\t' + snippet + '\n'
    else:
        for value in info_dict[info]:
            report = report + ' ' + value
    report = report + '\n'
    return report


def print_base_invoke(base_image, base_tag):
    '''Given the base image and tag in a tuple return a string containing
    the command_lib/base.yml'''
    info = command_lib.command_lib.get_base_listing(base_image, base_tag)
    report = ''
    report = report + print_invoke_list(info, 'names')
    report = report + print_invoke_list(info, 'versions')
    report = report + print_invoke_list(info, 'licenses')
    report = report + print_invoke_list(info, 'src_urls')
    report = report + '\n'
    return report


def print_package_invoke(command_name):
    '''Given the command name to look up in the snippet library and the
    package name, return a string with the list of commands that will be
    invoked in the container'''
    report = ''
    command_listing = command_lib.command_lib.get_command_listing(command_name)
    if command_listing:
        pkg_list = command_listing['packages']
        for pkg_dict in pkg_list:
            report = report + print_invoke_list(pkg_dict, 'version')
            report = report + print_invoke_list(pkg_dict, 'license')
            report = report + print_invoke_list(pkg_dict, 'src_url')
            report = report + print_invoke_list(pkg_dict, 'deps')
    return report


def print_package(pkg_obj, prefix):
    '''Given a Package object, print out information with a prefix'''
    notes = formats.package_demarkation
    notes = notes + prefix + formats.package_name.format(
        package_name=pkg_obj.name)
    notes = notes + prefix + formats.package_version.format(
        package_version=pkg_obj.version)
    notes = notes + prefix + formats.package_url.format(
        package_url=pkg_obj.src_url)
    notes = notes + prefix + formats.package_license.format(
        package_license=pkg_obj.license)
    notes = notes + '\n'
    return notes


def print_notices(notice_origin, origin_pfx, notice_pfx):
    '''Given a NoticeOrigin object with a prefix (like a series of tabs)
    for the origin and the notice messages, return the notes'''
    notes = origin_pfx + notice_origin.origin_str + ':\n'
    for notice in notice_origin.notices:
        notes = notes + notice_pfx + notice.level + ': ' + \
            notice.message + '\n'
    return notes


def print_full_report(image):
    '''Given an image, go through the Origins object and collect all the
    notices for the image, layers and packages'''
    notes = ''
    for image_origin in image.origins.origins:
        notes = notes + print_notices(image_origin, '', '\t')
    for layer in image.layers:
        if layer.import_image:
            notes = notes + print_full_report(layer.import_image)
        else:
            for layer_origin in layer.origins.origins:
                notes = notes + print_notices(layer_origin, '\t', '\t\t')
            for package in layer.packages:
                notes = notes + print_package(package, '\t\t')
                for package_origin in package.origins.origins:
                    notes = notes + print_notices(
                        package_origin, '\t\t', '\t\t\t')
            notes = notes + formats.package_demarkation
    return notes


def print_summary_report(image):
    '''Given an image, only print the package information'''
    notes = ''
    for layer in image.layers:
        if layer.import_image:
            notes = notes + print_summary_report(layer.import_image)
        else:
            for package in layer.packages:
                notes = notes + print_package(package, '')
            notes = notes + formats.package_demarkation
    return notes
