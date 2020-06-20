# source the virtual env
source venv/bin/activate && \
    # create output dir
    mkdir -p dist/{css,assets,fonts,scripts} && \
    # create assets dir
    #mkdir -p dist/assets && \
    # compile scss
    pysassc assets/scss/styles.scss dist/css/styles.css && \
    # compile minified scss
    pysassc --style compressed assets/scss/styles.scss dist/css/styles.min.css && \
    # copy scripts
    cp -r assets/scripts dist/ && \
    # copy fonts
    cp -r assets/fonts dist/
    # copy default favicon
    cp assets/_default.png dist/assets