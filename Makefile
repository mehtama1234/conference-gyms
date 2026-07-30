.PHONY: validate validate-lanes validate-terminaltraj validate-cybergym validate-openapps publication-check replay-terminaltraj

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
