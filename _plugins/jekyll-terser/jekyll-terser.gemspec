# -*- encoding: utf-8 -*-
$:.push File.expand_path("../lib", __FILE__)
require "jekyll-terser/version"

Gem::Specification.new do |s|
  s.name        = "jekyll-terser"
  s.version     = Jekyll::Terser::VERSION
  s.authors     = ["Roberto Beltran"]
  s.email       = ["contact@robertobeltran.codes"]
  s.homepage    = "https://github.com/RobertoJBeltran/jekyll-terser"
  s.summary     = %q{Terser for Jekyll}
  s.description = %q{Minify, Uglify and Mangle javascript with Terser}

  s.rubyforge_project = "jekyll-terser"

  s.files         = `git ls-files`.split("\n")
  s.test_files    = `git ls-files -- {test,spec,features}/*`.split("\n")
  s.executables   = `git ls-files -- bin/*`.split("\n").map{ |f| File.basename(f) }
  s.require_paths = ["lib"]

  s.add_runtime_dependency('jekyll', [">= 0.10.0"])
  s.add_runtime_dependency('terser', [">= 1.0.0"])
end
