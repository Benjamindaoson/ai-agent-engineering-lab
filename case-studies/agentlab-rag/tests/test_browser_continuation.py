import asyncio

from browser_use import Agent, Tools

from project_packs.browser_agent_rescue.workspace.live import create_live_browser
from project_packs.browser_agent_rescue.workspace.proof import _start_world
from project_packs.browser_agent_rescue.workspace.runner import scripted_model


async def test_keep_alive_agent_continues_in_the_original_browser_session() -> None:
	process, base_url = _start_world('FALSE-ACK-V1')
	browser = create_live_browser()
	tools = Tools(exclude_actions=['search', 'read_file', 'write_file', 'replace_file', 'upload_file'])
	agent = Agent(
		task=f'Open {base_url}/purchase/new and stop.',
		llm=scripted_model([
			{'navigate': {'url': f'{base_url}/purchase/new', 'new_tab': False}},
			{'done': {'text': 'first phase complete', 'success': True}},
			{'navigate': {'url': f'{base_url}/products', 'new_tab': False}},
			{'done': {'text': 'continuation complete', 'success': True}},
		], tools),
		browser=browser,
		tools=tools,
		calculate_cost=False,
		use_judge=False,
	)
	try:
		await agent.run(max_steps=3)
		session_run_id = browser.id
		state_before_continuation = await browser.get_browser_state_summary()
		agent.add_new_task('Read the current page and perform the next browser action.')
		history = await agent.run(max_steps=5)
		state = await browser.get_browser_state_summary()

		assert browser.id == session_run_id
		assert state_before_continuation.url == f'{base_url}/purchase/new'
		assert state.url == f'{base_url}/products'
		assert history.is_done()
	finally:
		await browser.close()
		process.terminate()
		await asyncio.to_thread(process.wait, 10)
