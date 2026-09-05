# frozen_string_literal: true

# Zotero exports sometimes paste the same entry twice (same key + same title).
# BibTeX-Ruby then auto-renames later copies, inventing keys. Strip true
# duplicates from the raw .bib before Scholar loads it. Same-key / different-
# title collisions are kept (with a warning) so distinct papers are not lost.
module DedupeBibliography
  ENTRY_START = /^@\w+\{/
  KEY_PATTERN = /^@\w+\{\s*([^,\s]+)\s*,/
  TITLE_PATTERN = /^\s*title\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}/i

  module_function

  def bib_path(site)
    source = (site.config.dig('scholar', 'source') || '_bibliography').to_s.sub(%r{\A/}, '')
    filename = site.config.dig('scholar', 'bibliography') || 'papers.bib'
    File.join(site.source, source, filename)
  end

  def split_entries(content)
    chunks = content.split(/(?=^@\w+\{)/)
    preamble = []
    entries = []
    chunks.each do |chunk|
      if chunk.match?(ENTRY_START)
        entries << chunk
      else
        preamble << chunk unless chunk.strip.empty?
      end
    end
    [preamble.join, entries]
  end

  def citation_key(entry)
    match = entry.match(KEY_PATTERN)
    match && match[1]
  end

  def normalized_title(entry)
    match = entry.match(TITLE_PATTERN)
    return '' unless match

    match[1].gsub(/[{}]/, '').gsub(/\s+/, ' ').strip.downcase
  end

  def dedupe_content(content)
    preamble, entries = split_entries(content)
    seen = {}
    dropped = Hash.new(0)
    key_titles = Hash.new { |h, k| h[k] = [] }
    kept = []

    entries.each do |entry|
      key = citation_key(entry)
      title = normalized_title(entry)
      if key.nil?
        kept << entry
        next
      end

      key_titles[key] << title unless key_titles[key].include?(title)
      fingerprint = [key, title]
      if seen[fingerprint]
        dropped[key] += 1
        next
      end
      seen[fingerprint] = true
      kept << entry
    end

    collisions = key_titles.select { |_key, titles| titles.size > 1 }
    [preamble + kept.join, dropped, collisions]
  end
end

Jekyll::Hooks.register :site, :after_init do |site|
  path = DedupeBibliography.bib_path(site)
  next unless File.exist?(path)

  content = File.read(path, encoding: 'UTF-8')
  deduped, dropped, collisions = DedupeBibliography.dedupe_content(content)
  next if dropped.empty? && collisions.empty?

  dropped.each do |key, count|
    Jekyll.logger.warn 'dedupe_bibliography:',
                       "duplicate entry #{key} (#{count + 1} copies) — keeping one"
  end
  collisions.each do |key, titles|
    Jekyll.logger.warn 'dedupe_bibliography:',
                       "citation key collision #{key}: #{titles.size} different titles — " \
                       'keeping all; fix keys in Zotero'
  end

  next if dropped.empty?

  out_dir = File.dirname(path)
  out_name = 'papers.deduped.bib'
  out_path = File.join(out_dir, out_name)
  File.write(out_path, deduped, encoding: 'UTF-8')
  site.config['scholar'] ||= {}
  site.config['scholar']['bibliography'] = out_name
end
