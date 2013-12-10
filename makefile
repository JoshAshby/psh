BOOTSTRAP_LESS = ./interface/static/less/bootstrap/bootstrap.less
BOOTSTRAP_ADMIN_LESS = ./interface/static/less/bootstrap/AnotherAdminBootstrap.less
BOOTSTRAP_RESPONSIVE_LESS = ./interface/static/less/bootstrap/responsive.less
FONTAWESOME_LESS = ./interface/static/less/fontawesome/font-awesome.less
CUSTOM_LESS = ./interface/static/less/custom_styles.less
BOOTSTRAP_MARKDOWN = ./interface/static/less/bootstrap-markdown.less
COFFEE_DIR = ./interface/static/cs/
CHECK=✔

flagr: bootstrap less coffee
	@echo "You should link interface/static to your servers /static/"
	@echo "In other words, interface/static should be accessible from localhost/static"

bootstrap:
	@echo "Compiling Twitter Bootstrap..."
	mkdir -p interface/static/css/bootstrap
	./node_modules/.bin/recess --compile ${BOOTSTRAP_LESS} > interface/static/css/bootstrap/bootstrap.css
	./node_modules/.bin/recess --compress ${BOOTSTRAP_LESS} > interface/static/css/bootstrap/bootstrap.min.css
	./node_modules/.bin/recess --compile ${BOOTSTRAP_ADMIN_LESS} > interface/static/css/bootstrap/adminBootstrap.css
	./node_modules/.bin/recess --compress ${BOOTSTRAP_ADMIN_LESS} > interface/static/css/bootstrap/adminBootstrap.min.css
	./node_modules/.bin/recess --compile ${BOOTSTRAP_RESPONSIVE_LESS} > interface/static/css/bootstrap/bootstrap-responsive.css
	./node_modules/.bin/recess --compress ${BOOTSTRAP_RESPONSIVE_LESS} > interface/static/css/bootstrap/bootstrap-responsive.min.css
	@echo "Done ${CHECK}"
	@echo "Compiling Font-Awesome for Bootstrap..."
	mkdir -p interface/static/css/fontawesome
	./node_modules/.bin/recess --compile ${FONTAWESOME_LESS} > interface/static/css/fontawesome/fontawesome.css
	./node_modules/.bin/recess --compress ${FONTAWESOME_LESS} > interface/static/css/fontawesome/fontawesome.min.css
	@echo "Done ${CHECK}"

less:
	@echo "Compiling custom LESS..."
	./node_modules/.bin/recess --compile ${CUSTOM_LESS} > interface/static/css/custom_styles.css
	./node_modules/.bin/recess --compress ${CUSTOM_LESS} > interface/static/css/custom_styles.css
	./node_modules/.bin/recess --compile ${BOOTSTRAP_MARKDOWN} > interface/static/css/bootstrap-markdown.css
	./node_modules/.bin/recess --compress ${BOOTSTRAP_MARKDOWN} > interface/static/css/bootstrap-markdown.css
	@echo "Done ${CHECK}"

coffee:
	@echo "Compiling CoffeeScript..."
	./node_modules/.bin/coffee --compile --output interface/static/js/ ${COFFEE_DIR}
	@echo "Done ${CHECK}"

clean:
	@echo "Cleaning up a few directories I made..."
	rm -rf interface/static/css/bootstrap
	rm -rf interface/static/css/fontawesome
	rm -rf flagr_core/views
	@echo "Done ${CHECK}"

