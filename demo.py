#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import itertools
import tinycss2
import re

def readCSS(filename):
    result = {}
    data = open(filename, 'r').read()
    css  = tinycss2.parse_stylesheet(data, skip_whitespace=True)
    
    for style in css:
        if style.type == 'qualified-rule':        
            selector     = ''.join([t.serialize() for t in style.prelude]).strip().strip('.')
            declarations = ''.join([t.serialize() for t in style.content]).strip()
            declarations = re.sub(r'\s+', ' ', declarations).strip()
            
            if ':' in selector or ' ' in selector or '.' in selector:
                continue
            
            if declarations not in result:
                result[declarations] = []
            result[declarations].append(selector)
        elif style.type == 'at-rule':            
            selector     = ''.join([t.serialize() for t in style.prelude]).strip().strip('.')
            declarations = ''.join([t.serialize() for t in style.content]).strip()
            
            childStyles = tinycss2.parse_stylesheet(declarations)
            for childStyle in childStyles:
                if childStyle.type != 'qualified-rule': 
                    continue
                
                childSelector     = ''.join([t.serialize() for t in childStyle.prelude]).strip().strip('.')
                childDeclarations = selector + ';' + ''.join([t.serialize() for t in childStyle.content]).strip()
                
                if ' ' in childSelector or '.' in childSelector:
                    continue
                
                if childDeclarations not in result:
                    result[childDeclarations] = []
                result[childDeclarations].append(childSelector)
        
    return result

def createMapping(obfuscatedRules, normalRules):
    mapping = {}
    
    for style, obfuscatedSelectors in obfuscatedRules.items():
        normalSelectors = normalRules.get(style, [])
        if not normalSelectors:
            print('no match for', style)
            continue
            
        for obfuscatedSelector in obfuscatedSelectors:
            # process obfuscated class only
            if len(obfuscatedSelector) != 5:
                continue
            elif len(normalSelectors) == 1:
                mapping[obfuscatedSelector] = normalSelectors[0]
            else:
                print(f'found {len(normalSelectors)} matches', normalSelectors)
                mapping[obfuscatedSelector] = normalSelectors[0]

    return mapping

def deobfuscateClass(classNames, classMapping):
    results = []
    for row in re.split(r'\s+', classNames):
        if row in classMapping:
            results.append(classMapping[row].replace('\\', ''))
        else:
            results.append(row)
            
    return ' '.join(results)

obfuscatedRules = readCSS('obfuscated.css')
normalRules = readCSS('original.css')

mapping = createMapping(obfuscatedRules, normalRules)

testClass = 'xxxxx'
actualClass = deobfuscateClass(testClass, mapping)

print(testClass)
print(actualClass)
