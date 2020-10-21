#!/usr/bin/env python3
# usage: python3 run_matcher_linux.py <from_version> <to_version>
# You may have to temporarily set the JAVA_HOME if your default is 8.
# from_version should be the older version of the two.

import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

def update(from_version, to_version):
	if not os.path.exists('Matcher'):
		subprocess.call(['git', 'clone', 'https://github.com/FabricMC/Matcher.git'])
		subprocess.call(['./gradlew build'], cwd='Matcher/', shell=True)
		os.remove('Matcher/settings.gradle')
	os.chdir('Matcher')
	if not os.path.exists('yarn'):
		os.mkdir('yarn')
	download_version(from_version)
	download_version(to_version)
	overwrite_matcher_config_list('paths-a', [os.path.abspath('yarn/' + from_version + '/' + from_version + '-merged.jar')])
	overwrite_matcher_config_list('paths-b', [os.path.abspath('yarn/' + to_version + '/' + to_version + '-merged.jar')])
	common_libs = set()
	libs_from = []
	libs_to = []
	for lib in os.listdir('yarn/' + from_version + '/.gradle/minecraft/libraries'):
		if os.path.exists('yarn/' + to_version + '/.gradle/minecraft/libraries/' + lib):
			common_libs.add(lib)
		else:
			libs_from.append(lib)
	for lib in os.listdir('yarn/' + to_version + '/.gradle/minecraft/libraries'):
		if lib not in common_libs:
			libs_to.append(lib)
	overwrite_matcher_config_list('paths-shared', [os.path.abspath('yarn/' + from_version + '/.gradle/minecraft/libraries/' + lib) for lib in common_libs])
	overwrite_matcher_config_list('class-path-a', [os.path.abspath('yarn/' + from_version + '/.gradle/minecraft/libraries/' + lib) for lib in libs_from])
	overwrite_matcher_config_list('class-path-b', [os.path.abspath('yarn/' + to_version + '/.gradle/minecraft/libraries/' + lib) for lib in libs_to])
	subprocess.Popen(['java', '-Xmx8g', '-jar', 'build/libs/matcher-all.jar'], cwd='../Matcher')

def download_version(version):
	if os.path.exists('yarn/' + version):
		shutil.rmtree('yarn/' + version)
	subprocess.call(['git', 'clone', 'https://github.com/FabricMC/yarn', version], cwd='yarn')
	with open('yarn/' + version + '/build.gradle') as f:
		lines = [line for line in f]
	with open('yarn/' + version + '/build.gradle', 'w') as f:
		for line in lines:
			if line.startswith('def minecraft_version'):
				f.write('def minecraft_version = "' + version + '"\n')
			elif line.lstrip().startswith('version.libraries.each'):
				f.write('version.libraries.findAll { it.downloads.artifact != null }.each {\n')
			else:
				f.write(line)
	subprocess.call('./gradlew mergeJars downloadMcLibs', cwd='yarn/' + version, shell=True)

def overwrite_matcher_config_list(key, elements):
	def update(root):
		while len(root) > 0:
			del root[0]
		for i in range(len(elements)):
			ET.SubElement(root, 'entry', key=str(i), value=elements[i])
	update_matcher_config(key, update)

def update_matcher_config(key, transformer):
	path = os.path.expanduser('~') + '/.java/.userPrefs/player-obf-matcher/last-project-setup/' + key + '/prefs.xml'
	if not os.path.exists(path):
		os.makedirs(os.path.dirname(path), exist_ok=True)
		root = ET.Element('map', attrib={'MAP_XML_VERSION': '1.0'})
		tree = ET.ElementTree(root)
	else:
		tree = ET.parse(path)
		root = tree.getroot()
	transformer(root)
	with open(path, 'w') as f:
		doctype = '<!DOCTYPE map SYSTEM "http://java.sun.com/dtd/preferences.dtd">\n'
		f.write(ET.tostring(root, encoding='utf8', method='xml').decode(encoding='utf8').replace('\n', '\n' + doctype, 1))

if __name__ == '__main__':
	update(sys.argv[1], sys.argv[2])

