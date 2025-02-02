import modules

class TheSimpleton(modules.Module):
	identifiers = ["simpleton", "thesimpleton"]
	display_name = "The Simpleton"
	manual_name = "The Simpleton"
	help_text = "Use `{cmd} push` to push the button and solve the module."
	module_score = 1
	
	def __init__(self, bomb, ident):
		super().__init__(bomb, ident)
	
	def get_svg(self, led):
		return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 348 348" fill="#fff"><path d="M5 6h337v337H5z" stroke-width="2" stroke="#000"/><path d="M283 41c0-9 7-16 15-16 4 0 8 2 11 5s5 7 5 11c0 8-7 15-16 15-8 0-15-7-15-15z" stroke-width="2" stroke="#000" fill="{0}"/><circle cx="165.8" cy="179.5" r="138.8" fill="#fff" stroke="#000" stroke-width="2.5"/><g aria-label="PUSH IT!" style="line-height:1.25;-inkscape-font-specification:\'Special Elite\'" font-weight="700" font-size="58.4" font-family="Special Elite" letter-spacing="0" word-spacing="0" fill="#000" stroke-width="1.8"><path d="M53 165v1l-1-1h1zm8 21v-1 1zm20-14v5l-1 1-1 2-1 1h-1l-1 1-4 2h-4-1-1-1-1l-1 1h-1l-1 1h2v1l-1 1v7l1 2h1l2 1v1h1l1 1-1 1v1H54l-1-1 1-2 1-1h1l1-1h1v-1-1-1-1-1-1-1-3-2-1-1-1-1-1-1-1-1-1-1-1-1-2-2-1h1l1-1h-1-2v-1h-1v-1h-1l-1 1v-1-1h-1l1-1 1-1h15l2 1h2l1 1h1l1 1 1 1h1v1l1 1v1h1v3zm-4 2l-1-3-1-3-3-1-3-1h-5l-1 1h-1l-1 1v1l1 1v5h-1v1l1 2 1 1h1l1 1h1l2-1h4v-1h3l1-1 1-1v-2zM119 163l-1 1-1 1h-1l-1 1h-2v2l-1 1-1 1 1 1v5l1 2h-1v3l1 3v2l-1 1v1l1 1v2l-1 2v1l-2 1v1l1 1h-1v1h-1v1h-1v1h-1l-1 1h-1l-2 1h-3l-1-1h-1-2-1l-1-1h-1l-1-1-1-1v-2l-1-2v-2-2l-1-2v-1-1-3l1-2-1-4v-3-1l1-1v-1-1l-1-1v-2-1l-1-1-2-1h-1l-1-1 1-1 1-1h10l2 1v2l-1 1-1 1-2 1v2l-1 1v14l-1 1h1v-1 1h1v7l1 1v1l1 1 1 1 1 1h1l1 1 1 1v1l1-1h1v1h1v-1-1h-1v-1h1l1-1h1l1-1v-1l1-1v-2-1-1l1-1-1-2v-1-1l1-1-1-1v-2-2l1-2-1-3v-2-1-1h1l-1-1h-1v-1-1h-1-1l-1-1h-1v-1l-1-2h1v-1h7l1-1 1 1h4l1 1h1v1h1zM151 188v5h-2v1h1v1l-1 1-1 1v1h-3v2h-2l-1 1h-2l-2 1-3 1-2-1h-1l-2-1h-2-1-1v1h-1l-1-1-1-1-1-2v-1-1l1-1-1-1v-2-1l1-1h-1v-1l1-1v-1-1-1l1 1 1 1 1 2v5l1 1h1l2 1 1 2h8l2-1 1-1 1-1 1-1h1l1-1v-1l1-1v-2-2l-1-1-1-1h-1l-1-1-1-1h-3l-1-1-1 1h-1l-1-1h-1-1-1l-1-1h-1l-3-2-1-1v-1h-1v-1l-1-1v-2l-1-1 1-1v-1-1h0v-1l1-1 1-1 1-1 1-1 1-1h2l1-1h9l1 1h2v-1h3v2l1 1v4h1l-1 1v6h-1-1v-1l-1-1v-1-1l-1-1-1-1v-1l-1-1h-1l-1-1h-1-1-1l-1-1-2 1h-1l-2 1-2 1v5l1 2 1 1h1l2 1h4l1 1h5v1h2l1 1 1 1 1 1v1l1 1v1h1v2zM190 200v1h-2l-1 1h-3-3l-1 1h-2v-1h-2l-1-1v-1l1-1 1-1h2l1 1v-1-1h1v-1-2-1-1-1-1-1-1-1-1l-1-1v-1l-1-1h-4-2-1l-1 1h-2-2l-1 1v4l-1 1v1l1 1-1 1v1l1 1v1l1 1 1 1h1l2 1v3h-1l-1 1h-1l-1-1-4 1h-3-1l-1-1h-2v-1-1-1h1v-1h2l1-1 1-1 1-2v-2-1-1-1-2l-1-3 1-1v-1l-1-1v-1-1l1-1v-1-1-1-1-1-1h-1v-1h1v-1-1l-1-1v-1h-1l-1-1h-2l-1-1v-1-1l1-1h12v1l1 1v1h-1-1l-2 1-1 1v4l1 2-1 2v1l1 2 1 1h7l1 1h3v-1h2v-1l1-1v-1-1-1l-1-1v-1-1-1-1-2l-1-1h-3l-1-1-1-1v-1l1-1h12l2 1v2l-1 1h-2l-1 1h-1v20l1 2-1 1v1l1 1-1 2v1l1 1v1l1 1h1l1 1h2v1zM236 164v1h-1v1h-1-1-1-1-2-1v1l-1 1h-1v28l1 1h1l1 1 3-1h2l1 1 1 1v2l-1 1-1 1h-16l-1-1h-1l-1 1h-1-1l-2-1-1-1 1-1v-1l1-1 1-1v1h4l2-1 2-1 1-2-1-1v-1-3-3-2l1-2-1-1v-1-1-1-1-2l1-2-1-1v-2-1-1-1h-1v-1h-1l-1-1v1h-1l-1 1h-2-1l-1-1h-1l-1-1 1-1v-1l1-1 1-1h11v-1l1 1h2v-1l1 1v1l1-1h1l1 1h1l-1-1h1l1-1v1h2v2h1v1zm-14 2v-1h-1v2h1v-1zM271 172v2l-1 1-1 1h-1v-1-1h-1v-1l-1-1v-1-1l-1-2 1-1v-1-1l-1-1h-4-1l-2 1h-1v10l1 2v2l-1 3 1 1v5h-1l1 1v1l-1 1 1 1v2l1 1 1 1h4l1 1v3h-1v1l-1-1h-1l-3 1h-3l-3 1h-3-1l-1-1h-2v-1-1-1h2l-1-1h3l1-1h2v-1-1l1-1-1-3v-2-1l1-1-1-1v-1-1-2-1-1-4-4-5-1h-1l-2-1h-4l-1 1-2 1v8h-1v2h-1-1v-1-1-1-1-1-1-1l-1-2v-2l1-2 1-2h27l2 1v6l1 2v2zM285 169l-1 1v5l-1 1v9l-1 1v2h1l-1 1v1l-1 1h-1l-1-1v-1-1-1-2-1-1l-1-1v-1-3-2-3-2l-1-2v-2-1l1-1v-2l1-1 1-1h2v1h1l1 1v5l1 1zm-2 29v2l-1 1-1 1h-2l-1-1-1-1v-2l1-2 3-1h1l1 1v2z"/></g></svg>'.format(led)

	@modules.check_solve_cmd
	@modules.noparts
	async def push_cmd(self, author):
		self.log("Button pushed, solving module")
		await self.handle_solve(author)
	
	COMMANDS = {
		"push": push_cmd
	}
