# where do you want to put the CSS stylesheet for the website?
CUSTOM_BOOTSTRAP_CSS_TARGET_DIRECTORY="./furfolio/static/style"
CUSTOM_BOOTSTRAP_CSS_TARGET_FILE="${CUSTOM_BOOTSTRAP_CSS_TARGET_DIRECTORY}/style.css"
# where do you want to place the bootstrap javascript file?
BOOTSTRAP_JS_TARGET_DIRECTORY="./furfolio/static/js"
BOOTSTRAP_JS_TARGET_FILE="${BOOTSTRAP_JS_TARGET_DIRECTORY}/bootstrap.bundle.min.js"
BOOTSTRAP_JS_TARGET_MAP_FILE="${BOOTSTRAP_JS_TARGET_DIRECTORY}/bootstrap.bundle.min.js.map"
# where is the bootstrap source?
BOOTSTRAP_SOURCE_DIR="./bootstrap-5.3.2"

# clear javascript in case bootstrap source changed.
rm -rf ./furfolio/static/js/

# make directories for the directories that hold the generated static CSS and js files for the site.
mkdir -p $CUSTOM_BOOTSTRAP_CSS_TARGET_DIRECTORY
mkdir -p $BOOTSTRAP_JS_TARGET_DIRECTORY

cp $BOOTSTRAP_SOURCE_DIR/dist/js/bootstrap.bundle.min.js $BOOTSTRAP_JS_TARGET_FILE
cp $BOOTSTRAP_SOURCE_DIR/dist/js/bootstrap.bundle.min.js.map $BOOTSTRAP_JS_TARGET_MAP_FILE
sass --watch ./furfolio/sass/furfolio-theme.scss  $CUSTOM_BOOTSTRAP_CSS_TARGET_FILE