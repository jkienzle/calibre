# -*- coding: utf-8 -*-
# Copyright (C) 2006-2007 Søren Roug, European Environment Agency
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Contributor(s):
#

from __future__ import print_function, unicode_literals, absolute_import, division
from .namespaces import NUMBERNS
from .element import Element
from .style import StyleElement


# Autogenerated
def AmPm(**args):
    return Element(qname=(NUMBERNS,'am-pm'), **args)


def Boolean(**args):
    return Element(qname=(NUMBERNS,'boolean'), **args)


def BooleanStyle(**args):
    return StyleElement(qname=(NUMBERNS,'boolean-style'), **args)


def CurrencyStyle(**args):
    return StyleElement(qname=(NUMBERNS,'currency-style'), **args)


def CurrencySymbol(**args):
    return Element(qname=(NUMBERNS,'currency-symbol'), **args)


def DateStyle(**args):
    return StyleElement(qname=(NUMBERNS,'date-style'), **args)


def Day(**args):
    return Element(qname=(NUMBERNS,'day'), **args)


def DayOfWeek(**args):
    return Element(qname=(NUMBERNS,'day-of-week'), **args)


def EmbeddedText(**args):
    return Element(qname=(NUMBERNS,'embedded-text'), **args)


def Era(**args):
    return Element(qname=(NUMBERNS,'era'), **args)


def Fraction(**args):
    return Element(qname=(NUMBERNS,'fraction'), **args)


def Hours(**args):
    return Element(qname=(NUMBERNS,'hours'), **args)


def Minutes(**args):
    return Element(qname=(NUMBERNS,'minutes'), **args)


def Month(**args):
    return Element(qname=(NUMBERNS,'month'), **args)


def Number(**args):
    return Element(qname=(NUMBERNS,'number'), **args)


def NumberStyle(**args):
    return StyleElement(qname=(NUMBERNS,'number-style'), **args)


def PercentageStyle(**args):
    return StyleElement(qname=(NUMBERNS,'percentage-style'), **args)


def Quarter(**args):
    return Element(qname=(NUMBERNS,'quarter'), **args)


def ScientificNumber(**args):
    return Element(qname=(NUMBERNS,'scientific-number'), **args)


def Seconds(**args):
    return Element(qname=(NUMBERNS,'seconds'), **args)


def Text(**args):
    return Element(qname=(NUMBERNS,'text'), **args)


def TextContent(**args):
    return Element(qname=(NUMBERNS,'text-content'), **args)


def TextStyle(**args):
    return StyleElement(qname=(NUMBERNS,'text-style'), **args)


def TimeStyle(**args):
    return StyleElement(qname=(NUMBERNS,'time-style'), **args)


def WeekOfYear(**args):
    return Element(qname=(NUMBERNS,'week-of-year'), **args)


def Year(**args):
    return Element(qname=(NUMBERNS,'year'), **args)
