# Read More Tag Plugin for Jekyll
# Allows markdown processing inside collapsible content blocks

module Jekyll
  module Tags
    class ReadMoreTag < Liquid::Block
      def initialize(tag_name, markup, tokens)
        super
        # Parse attributes: read_more="Read more" read_less="Show less"
        @read_more_text = 'Read more'
        @read_less_text = 'Show less'
        
        if markup && !markup.empty?
          # Extract data-read-more value
          if markup =~ /read_more\s*=\s*["']([^"']+)["']/i
            @read_more_text = $1
          end
          # Extract data-read-less value
          if markup =~ /read_less\s*=\s*["']([^"']+)["']/i
            @read_less_text = $1
          end
        end
      end

      def render(context)
        site = context.registers[:site]
        converter = site.find_converter_instance(::Jekyll::Converters::Markdown)
        body = converter.convert(super(context))
        "<div data-read-more=\"#{@read_more_text}\" data-read-less=\"#{@read_less_text}\">#{body}</div>"
      end
    end
  end
end

Liquid::Template.register_tag('read_more', Jekyll::Tags::ReadMoreTag)










