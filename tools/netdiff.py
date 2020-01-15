#!/usr/bin/env python3

# Copyright (c) 2019 Jon Evans <jon@craftyjon.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This utility compares two netlists generated by Eeschema and reports on
# connectivity differences between them.  This only is looking at connectivity!
# Things like the components section, the visual format of the file, and the
# sorting of entries is not compared.

import argparse
import json
import os
import sexpdata
import sys


def extract_nets(sexpr):
    # Starts with ( export (version N) (...) )
    for idx, key in enumerate(sexpr):
        # print("{}: {}".format(idx, key))
        if isinstance(key, list):
            if isinstance(key[0], sexpdata.Symbol) and key[0].value() == "nets":
                return key[1:]
    return None


def unpack(sexpr):
    ret = {}
    for net in sexpr:
        code = net[1][1]
        name = net[2][1]
        if isinstance(name, sexpdata.Symbol):
            name = name.value()
        name = str(name)

        members = []
        if len(net) < 4:
            continue

        for node in net[3:]:
            ref = node[1][1]
            pin = node[2][1]

            if isinstance(ref, sexpdata.Symbol):
                ref = ref.value()

            if isinstance(pin, sexpdata.Symbol):
                pin = pin.value()

            ref = str(ref)
            pin = str(pin)

            members.append((ref, pin))

        members.sort()
        ret[name] = members

    return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare KiCad netlists')
    parser.add_argument('first_netlist')
    parser.add_argument('second_netlist')

    args = parser.parse_args()

    fn_a = args.first_netlist
    fn_b = args.second_netlist

    with open(fn_a, 'r') as f:
        a = sexpdata.load(f)

    with open(fn_b, 'r') as f:
        b = sexpdata.load(f)

    # Extract the nets portion
    a = extract_nets(a)
    b = extract_nets(b)

    if a is None:
        print("Could not read nets from {}".format(fn_a))
        sys.exit(1)

    if b is None:
        print("Could not read nets from {}".format(fn_b))
        sys.exit(1)

    nets_a = unpack(a)
    nets_b = unpack(b)

    sa = set(nets_a.keys())
    sb = set(nets_b.keys())

    only_a = sa - sb
    only_b = sb - sa
    both = sa & sb

    if len(only_a) == len(only_b) == 0:
        print("{} and {} are identical".format(fn_a, fn_b))
        sys.exit(0)

    print("A: {}\nB: {}".format(fn_a, fn_b))

    changed_header = False

    for net_name in sorted(both):
        if nets_a[net_name] != nets_b[net_name]:
            if not changed_header:
                print("\nChanged nets:\n")
                changed_header = True

            print("{}: {} => {}".format(net_name, nets_a[net_name],
                                        nets_b[net_name]))

    discards_a = set()
    discards_b = set()

    renamed_header = False

    for net_name in sorted(only_a):
        for candidate in only_b:
            if nets_a[net_name] == nets_b[candidate]:
                if not renamed_header:
                    print("\nRenamed nets (no connection changes):\n")
                    renamed_header = True

                print("{} => {}".format(net_name, candidate))
                discards_a.add(net_name)
                discards_b.add(candidate)

    only_a.difference_update(discards_a)
    only_b.difference_update(discards_b)

    if len(only_a) > 0:
        print("\nOnly in {}:\n".format(fn_a))
        print('\n'.join(["{}: {}".format(el, nets_a[el])
                        for el in sorted(only_a)]))

    if len(only_b) > 0:
        print("\nOnly in {}:\n".format(fn_b))
        print('\n'.join(["{}: {}".format(el, nets_b[el])
                        for el in sorted(only_b)]))
