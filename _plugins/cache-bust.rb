# based on https://distresssignal.org/busting-css-cache-with-jekyll-md5-hash
# https://gist.github.com/BryanSchuetz/2ee8c115096d7dd98f294362f6a667db
module Jekyll
  module CacheBust
    class CacheDigester
      require 'digest/md5'
      require 'pathname'

      attr_accessor :file_name, :directory, :extra_files

      def initialize(file_name:, directory: nil, extra_files: [])
        self.file_name = file_name
        self.directory = directory
        self.extra_files = extra_files
      end

      def digest!
        [file_name, '?', Digest::MD5.hexdigest(file_contents)].join
      end

      private

      def directory_files_content
        target_path = File.join(directory, '**', '*')
        Dir[target_path].map{|f| File.read(f) unless File.directory?(f) }.join
      end

      def extra_files_content
        extra_files.map { |path| File.read(path) if File.file?(path) }.join
      end

      def file_content
        local_file_name = file_name.slice((file_name.index('assets/')..-1))
        File.read(local_file_name)
      end

      def file_contents
        parts = []
        parts << (directory.nil? ? file_content : directory_files_content)
        parts << extra_files_content
        parts.join
      end
    end

    def bust_file_cache(file_name)
      CacheDigester.new(file_name: file_name, directory: nil).digest!
    end

    def bust_css_cache(file_name)
      CacheDigester.new(
        file_name: file_name,
        directory: '_sass',
        extra_files: ['assets/css/main.scss']
      ).digest!
    end
  end
end

Liquid::Template.register_filter(Jekyll::CacheBust)