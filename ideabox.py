#! /usr/bin/python3.8

import re
import requests
import lxml.html
import json

SOURCES = {}

class DataSource:
	def __init__(self, name, baseurl):
		self.name = name
		self.baseurl = baseurl
		SOURCES[self.name] = self

	def listPagedIdeas(category, pageno):
		pass

	def listAllIdeas(category):
		pass

class OriginSource(DataSource):
	def __init__(self):
		super().__init__("origin", "https://ideabox.cio.go.jp")

	def fromUrl(self, url):
		match = re.search(r"/ja/idea/([0-9]+)", url)
		# TODO: add error check.
		no = match.group(1)
		html = get_html(f"{url}?d=100")
		html.make_links_absolute(self.baseurl)
		title = html.xpath("//h1[@class='topic_title']/span")[0].text
		match = re.search(r"[?&]category=([-_0-9A-Za-z]+)", html.xpath("//dl[@id='idea-cat']/dd/a")[0].get("href"))
		# TODO: add error check.
		category = match.group(1)
		author_tag = html.xpath("//dl[@id='idealist']/a")
		if (len(author_tag) > 0):
			author_tag = author_tag[0]
			match = re.search(r"ja/user/([-0-9a-f]+)", author_tag.get("href"))
			# TODO: add error check.
			author_no = match.group(1)
			author_name = author_tag.xpath(".//dd")[0].text
		else:
			author_no = "deadbeef-dead-beef-dead-beefdeadbeef"
			author_name = html.xpath("//dl[@id='idealist']//dd")[0].text
		author = Author(self, author_no, False, author_name)
		comments = []
		for tag in html.xpath("//section[@class='runway']/div[contains(@class, 'comment-container')]"):
			comment_no = tag.get("data-serial_number")
			message = "".join(tag.xpath(".//p")[0].itertext())
			commentator = tag.xpath(".//dl//a")
			if (len(commentator) > 0):
				commentator = commentator[0]
				match = re.search(r"ja/user/([-0-9a-f]+)", commentator.get("href"))
				# TODO: add error check.
				author_no = match.group(1)
				author_name = commentator.xpath(".//span")[0].text
			else:
				author_no = "deadbeef-dead-beef-dead-beefdeadbeef"
				author_name = "".join(tag.xpath(".//dt")[0].itertext())
			comment = Comment(self, comment_no, False, message, Author(self, author_no, False, author_name))
			comments.append(comment)
		return(Idea(self, no, False, title, category, author, comments))

	def listPagedIdeas(self, category, pageno):
		html = get_html(f"{self.baseurl}/ja/idea/?category={category}&order=date&d=10&p={pageno}")
		html.make_links_absolute(self.baseurl)
		ideas = list()
		for article in html.xpath("//article[@class='topic']/header/h2/a"):
			idea = self.fromUrl(article.get("href"))
			print(idea)
			for comment in idea.comments():
				print(f"  {comment}")
			ideas.append(idea)
		return(ideas)

	def listAllIdeas(category):
		# TODO: add implements.
		pass

class GoTo2chSource:
	def __init(self):
		super().__init__(self, "goto2ch", "http://goto2ch.net")

class Jsonable:
	def __init__(self, source, no, deleted):
		self.source = source
		self.no = no
		self.deleted = deleted

	def toJson(self):
		json = { "source": self.source }
		json["no"] = self.no
		json["deleted"] = self.deleted

	def toJsonString(self):
		return(json.dumps(self.toJson()))

class Author(Jsonable):
	def __init__(self, source, no, deleted, name):
		super().__init__(source, no, deleted)
		self.name = name.strip()

	def __str__(self):
		return(f"{self.name}#{self.no}")

class Idea(Jsonable):
	def __init__(self, source, no, deleted, title, category, author, comments):
		super().__init__(source, no, deleted)
		self.title = title
		self.category = category
		self.author = author
		self._comments = Comments(self)
		for comment in comments:
			self._comments.put(comment)

	def comments(self):
		return(self._comments.list())

	def __str__(self):
		return(f"Idea#{self.no}: [{self.author}] {self.title}")

class Comment(Jsonable):
	def __init__(self, source, no, deleted, message, author):
		super().__init__(source, no, deleted)
		self.message = message
		self.author = author

	def __str__(self):
		msg = self.message.replace("\n", "\\n")
		return(f"Comment#{self.no}: [{self.author}] {msg}")

class Comments:
	def __init__(self, idea):
		self.idea = idea
		self.comments = {}

	def put(self, comment):
		self.comments[comment.no] = comment

	def list(self):
		return(map(lambda x:x[1], sorted(self.comments.items(), key=lambda x:x[0])))

def get_html(url):
	r = requests.get(url)
	return(lxml.html.fromstring(r.text))

source = OriginSource()
for i in range(0, 10):
	source.listPagedIdeas("other", i)


