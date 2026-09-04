# frozen_string_literal: true

require 'bibtex'
require 'digest'

# Picks homepage publications: N newest selected entries, plus random
# remaining selected entries up to a max. The random draw is seeded by
# the build date so a given day is stable across CI runs.
module HomepagePublications
  MONTHS = {
    'jan' => 1, 'january' => 1,
    'feb' => 2, 'february' => 2,
    'mar' => 3, 'march' => 3,
    'apr' => 4, 'april' => 4,
    'may' => 5,
    'jun' => 6, 'june' => 6,
    'jul' => 7, 'july' => 7,
    'aug' => 8, 'august' => 8,
    'sep' => 9, 'september' => 9,
    'oct' => 10, 'october' => 10,
    'nov' => 11, 'november' => 11,
    'dec' => 12, 'december' => 12
  }.freeze

  module_function

  def selected?(entry)
    value = entry[:selected].to_s.strip.downcase
    %w[true 1 yes].include?(value)
  end

  def year_of(entry)
    entry[:year].to_s.to_i
  end

  def month_of(entry)
    raw = entry[:month].to_s.strip.downcase
    return raw.to_i if raw.match?(/\A\d+\z/)

    MONTHS[raw] || 0
  end

  def bib_path(site)
    source = (site.config.dig('scholar', 'source') || '_bibliography').to_s.sub(%r{\A/}, '')
    filename = site.config.dig('scholar', 'bibliography') || 'papers.bib'
    File.join(site.source, source, filename)
  end

  def query_for(keys)
    return '@*[selected=false]' if keys.empty?

    clauses = keys.map { |key| "key=#{key}" }.join(' || ')
    "@*[#{clauses}]"
  end
end

Jekyll::Hooks.register :site, :pre_render do |site|
  config = site.config['homepage_publications'] || {}
  max = Integer(config['max'] || 8)
  must_show = Integer(config['must_show'] || 4)
  max = 8 if max <= 0
  must_show = 4 if must_show <= 0
  must_show = max if must_show > max

  path = HomepagePublications.bib_path(site)
  unless File.exist?(path)
    Jekyll.logger.warn 'homepage_publications:', "bibliography not found at #{path}"
    site.data['homepage_publication_keys'] = []
    site.data['homepage_publication_query'] = '@*[selected=false]'
    next
  end

  bibliography = BibTeX.open(path)
  selected = bibliography.data.select do |entry|
    entry.is_a?(BibTeX::Entry) && HomepagePublications.selected?(entry)
  end

  selected.sort_by! do |entry|
    [-HomepagePublications.year_of(entry), -HomepagePublications.month_of(entry), entry.key.to_s]
  end
  selected.uniq! { |entry| entry.key.to_s }

  newest = selected.take(must_show)
  remainder = selected.drop(must_show)
  random_count = [max - must_show, remainder.size].min

  seed = site.time.strftime('%Y-%m-%d')
  seed_int = Digest::SHA256.hexdigest(seed)[0, 16].to_i(16)
  rng = Random.new(seed_int)
  random_picks = remainder.shuffle(random: rng).take(random_count)

  keys = (newest + random_picks).map { |entry| entry.key.to_s }
  site.data['homepage_publication_keys'] = keys
  site.data['homepage_publication_query'] = HomepagePublications.query_for(keys)
end

class HomepageBibliographyTag < Liquid::Tag
  def render(context)
    site = context.registers[:site]
    query = site.data['homepage_publication_query']
    query = '@*[selected=true]' if query.nil? || query.empty?
    markup = "--query #{query} --template bib_home --group_by none"
    parse_context = Liquid::ParseContext.new
    Jekyll::Scholar::BibliographyTag.send(:new, 'bibliography', markup, parse_context).render(context)
  end
end

Liquid::Template.register_tag('homepage_bibliography', HomepageBibliographyTag)
