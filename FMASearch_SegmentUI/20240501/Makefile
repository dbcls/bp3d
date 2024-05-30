DEV_HTDOCS := $(realpath ./htdocs)
DEV_JS := $(DEV_HTDOCS)/static/js/ag/
DEV_CSS := $(DEV_HTDOCS)/static/css/
DEV_OBJ := $(DEV_HTDOCS)/art_file/ $(DEV_HTDOCS)/MENU_SEGMENTS/
DEV_JSON := $(DEV_HTDOCS)/renderer_file/ $(DEV_HTDOCS)/MENU_SEGMENTS/

JAVA := /usr/bin/java
YUI := $(JAVA) -jar /bp3d/local/yuicompressor/build/yuicompressor-2.4.9.jar


JS_FILES := $(filter-out %.min.js, $(shell find $(DEV_JS) -depth -name "*.js" | sed 's/ /\\ /g'))
JS_TARGET_FILES := $(JS_FILES:%.js=%.min.js)

CSS_FILES := $(filter-out %.min.css, $(shell find $(DEV_CSS) -depth -name "*.css" | sed 's/ /\\ /g'))
CSS_TARGET_FILES := $(CSS_FILES:%.css=%.min.css)

OBJ_FILES := $(shell find $(DEV_OBJ) -depth -name "*.obj" | sed 's/ /\\ /g')
OBJ_TARGET_FILES := $(OBJ_FILES:%.obj=%.ogz)

JSON_FILES := $(shell find $(DEV_JSON) -depth -name "*.json" | sed 's/ /\\ /g')
JSON_TARGET_FILES := $(JSON_FILES:%.json=%.jgz)

.PHONY: all clean js clean_js css clean_css obj json

all: js css json

js: $(JS_FILES) $(JS_TARGET_FILES)

%.min.js: %.js
	$(YUI) --type js --nomunge -o $@ $<
	@chmod 0600 $<
	@chmod 0600 $@

css: $(CSS_FILES) $(CSS_TARGET_FILES)

%.min.css: %.css
	$(YUI) --type css --nomunge -o $@ $<
	@chmod 0600 $<
	@chmod 0600 $@

obj: $(OBJ_FILES) $(OBJ_TARGET_FILES)

%.ogz: %.obj
	gzip -c "$<" > "$@"
	@chmod 0600 "$<"
	@chmod 0600 "$@"

json: $(JSON_FILES) $(JSON_TARGET_FILES)

%.jgz: %.json
	gzip -c $< > $@
	@chmod 0600 $<
	@chmod 0600 $@


clean: clean_js clean_css

clean_js:
	rm -f $(JS_TARGET_FILES)

clean_css:
	rm -f $(CSS_TARGET_FILES)
