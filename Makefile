.PHONY: validate validate-lanes validate-terminaltraj validate-cybergym validate-openapps publication-check replay-terminaltraj replay-openapps-reward replay-openapps-browser probe-cybergym-server probe-cybergym-task-manifest probe-cybergym-broader-sample probe-cybergym-second-task-runtime audit-cybergym-arvo1065-stability

validate: validate-lanes

validate-lanes:
	@python3 scripts/validate_production_lanes.py

validate-terminaltraj:
	@python3 scripts/validate_terminaltraj_lane.py

validate-cybergym:
	@python3 scripts/validate_cybergym_lane.py

validate-openapps:
	@python3 scripts/validate_openapps_lane.py

publication-check:
	@python3 scripts/check_publication_ready.py

replay-terminaltraj:
	@python3 scripts/replay_terminaltraj_task_5279.py

replay-openapps-reward:
	@python3 scripts/replay_openapps_reward_fixture.py

replay-openapps-browser:
	@python3 scripts/replay_openapps_browser_task.py

probe-cybergym-server:
	@python3 scripts/probe_cybergym_server.py

probe-cybergym-task-manifest:
	@python3 scripts/run_cybergym_task_manifest_probe.py

probe-cybergym-broader-sample:
	@python3 scripts/probe_cybergym_broader_sample_readiness.py

probe-cybergym-second-task-runtime:
	@python3 scripts/run_cybergym_second_task_runtime_probe.py

audit-cybergym-arvo1065-stability:
	@python3 scripts/audit_cybergym_arvo1065_stability.py
