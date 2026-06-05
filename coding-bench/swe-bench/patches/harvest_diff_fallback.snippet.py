            progress_manager=progress_manager,
            instance_id=instance_id,
            **config.get("agent", {}),
        )
        info = agent.run(task)
        exit_status = info.get("exit_status")
        result = info.get("submission")
    except Exception as e:
        logger.error(f"Error processing instance {instance_id}: {e}", exc_info=True)
        exit_status, result = type(e).__name__, ""
        extra_info = {"traceback": traceback.format_exc(), "exception_str": str(e)}
    finally:
        # HARVEST_DIFF_FALLBACK: capture in-container git diff if submission empty (LimitsExceeded)
        if (not result or not str(result).strip()) and agent is not None:
            try:
                _env = getattr(agent, "env", None)
                if _env is not None:
                    _env.execute({"command": "git -C /testbed add -A"})
                    _d = _env.execute({"command": "git -C /testbed diff --cached"})
                    _patch = _d.get("output", "") if isinstance(_d, dict) else str(_d)
                    if _patch and _patch.strip():
                        result = _patch
                        exit_status = (str(exit_status) if exit_status else "") + "+HarvestedDiff"
                        logger.info(f"Harvested non-empty git diff for {instance_id} ({len(_patch)} bytes)")
            except Exception as _he:
                logger.error(f"diff harvest failed for {instance_id}: {_he}")
        if agent is not None:
            traj_path = instance_dir / f"{instance_id}.traj.json"
            agent.save(
                traj_path,
                {
                    "info": {
                        "exit_status": exit_status,
                        "submission": result,
                        **extra_info,
                    },
