all:
	@echo "install_requirements		install all required tools"
	@echo "pass_1					check out sources and update everything automatically"
	@echo "pass_2					create changelog and commit changes"
	@echo "pass_3					push changes and create a release draft"
	@echo "pass_4					upload documentation and close all branches"
	@echo "clean					delete generated files"
	@echo "veryclean				also delete checkout"

##########################################################
# requirements
##########################################################

install_requirements: homebrew_tools python_tools ruby_tools

homebrew_tools:
	brew install imagemagick python3 gnu-sed jq git-flow-avh coreutils

python_tools:
	rm -fr venv
	python3 -mvenv venv
	venv/bin/pip3 install -r requirements.txt

ruby_tools:
	gem install github_changelog_generator --user-install

uninstall_requirements:
	rm -fr venv

##########################################################
# passes
##########################################################

# do anything that can be done automatically
pass_1: clone_repository create_release_branch update_slideshow bump_version

# finalize release
#pass_2: update_changelog update_avatars check_documentation commit_changes
pass_2: update_avatars check_documentation commit_changes

# upload changes
pass_3: push_changes create_release_draft

# do release
pass_4: upload_documentation close_branches


##########################################################
# scripts
##########################################################

clone_repository:
	@echo "================================================================="
	@echo " Clone repository"
	@echo "================================================================="
	@echo ""
	scripts/clone/build.sh

create_release_branch:
	@echo ""
	@echo ""
	@echo "================================================================="
	@echo " Create release branch"
	@echo "================================================================="
	@echo ""
	-scripts/release_branch/build.sh

update_slideshow:
	@echo ""
	@echo ""
	@echo "================================================================="
	@echo " Update slideshow"
	@echo "================================================================="
	@echo ""
	make json.gif -C scripts/slideshow
	cp scripts/slideshow/json.gif workdir/json/docs
	cd workdir/json ; git add docs/json.gif

bump_version:
	@echo ""
	@echo ""
	@echo "================================================================="
	@echo " Bump version"
	@echo "================================================================="
	@echo ""
	cd scripts/bump_version	; ../../venv/bin/python3 bump_version.py ../../workdir/json

update_avatars:
	@echo ""
	@echo ""
	@echo "================================================================="
	@echo " Update avatars"
	@echo "================================================================="
	@echo ""
	mkdir -p scripts/avatars/cache
	cd scripts/avatars ; ../../venv/bin/python3 avatars.py ../../workdir/json/README.md
	cp scripts/avatars/avatars.png workdir/json/docs/avatars.png
	cd workdir/json ; git add docs/avatars.png

update_changelog:
	@echo ""
	@echo ""
	@echo "================================================================="
	@echo " Update changelog"
	@echo "================================================================="
	@echo ""
	cd scripts/changelog ; ./build.sh
	cp scripts/changelog/ChangeLog.md workdir/json
	cd workdir/json ; git add ChangeLog.md

check_documentation:
	@echo ""
	@echo ""
	@echo "================================================================="
	@echo " Check examples"
	@echo "================================================================="
	@echo ""
	make check_output_portable -j16 -C workdir/json/docs CXX=g++-12

commit_changes:
	@echo ""
	@echo ""
	@echo "================================================================="
	@echo " Commit changes"
	@echo "================================================================="
	@echo ""
	cd scripts/commit_changes ; ./commit_changes.sh

push_changes:
	@echo ""
	@echo ""
	@echo "================================================================="
	@echo " Push changes"
	@echo "================================================================="
	@echo ""
	cd scripts/push_changes ; ./push_changes.sh

create_release_draft:
	@echo ""
	@echo ""
	@echo "================================================================="
	@echo " Create release draft"
	@echo "================================================================="
	@echo ""
	make release -C workdir/json
	cd scripts/create_release_draft ; ../../venv/bin/python3 create_release_draft.py ../../workdir/json
	rm -fr workdir/json/release_files

upload_documentation:
	@echo ""
	@echo ""
	@echo "================================================================="
	@echo " Upload documentation"
	@echo "================================================================="
	@echo ""
	make install_venv publish -C workdir/json/docs/mkdocs

close_branches:
	@echo ""
	@echo ""
	@echo "================================================================="
	@echo " Closing branches"
	@echo "================================================================="
	@echo ""
	cd scripts/close_branches ; ./close_branches.sh

update_homebrew:
	@echo ""
	@echo ""
	@echo "================================================================="
	@echo " Closing branches"
	@echo "================================================================="
	@echo ""
	cd scripts/update_homebrew ; ./update_homebrew.sh

##########################################################
# cleanup
##########################################################

clean:
	make clean -C scripts/slideshow
	make clean -C workdir/json
	rm -f scripts/changelog/ChangeLog.md
	rm -f scripts/avatars/avatars.png

veryclean: clean
	rm -fr workdir/json
