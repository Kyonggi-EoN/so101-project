---
datasets: qkrtpah1/task1
library_name: lerobot
model_name: act
pipeline_tag: robotics
tags:
- act
- lerobot
- robotics
---

# Model Card for act

<!-- Provide a quick summary of what the model is/does. -->


[Action Chunking with Transformers (ACT)](https://huggingface.co/papers/2304.13705) is an imitation-learning method that predicts short action chunks instead of single steps. It learns from teleoperated data and often achieves high success rates.




<!-- A short demo is worth more than any description! Record a GIF/video of the policy
running on your robot, upload it to this repo, and embed it here:
<p align="center">
  <img src="https://huggingface.co/<hf_user>/<policy_repo_id>/resolve/main/demo.gif" width="60%"/>
</p>
-->

This policy has been trained and pushed to the Hub using [LeRobot](https://github.com/huggingface/lerobot).

Learn how to train and run it in the [LeRobot act guide](https://huggingface.co/docs/lerobot/main/en/act), or browse the [full documentation](https://huggingface.co/docs/lerobot/index).


---

## Model Details

- **License:** \[More Information Needed]
- **Robot type:** `so_follower`
- **Cameras:** `top`


## Inputs & Outputs

The policy consumes these observation features and produces these action features.

**Inputs**

| Feature | Type | Shape |
| --- | --- | --- |
| `observation.state` | STATE | `(6,)` |
| `observation.images.top` | VISUAL | `(3, 480, 640)` |

**Outputs**

| Feature | Type | Shape |
| --- | --- | --- |
| `action` | ACTION | `(6,)` |


## Training Dataset

- **Repository:** [qkrtpah1/task1](https://huggingface.co/datasets/qkrtpah1/task1)
- **Episodes:** 30
- **Frames:** 12969
- **Frame rate:** 30 FPS
- **Task(s):** "pick up the object"

<a class="flex" href="https://huggingface.co/spaces/lerobot/visualize_dataset?path=qkrtpah1/task1">
<img class="block dark:hidden" src="https://huggingface.co/datasets/huggingface/badges/resolve/main/visualize-this-dataset-xl.svg"/>
<img class="hidden dark:block" src="https://huggingface.co/datasets/huggingface/badges/resolve/main/visualize-this-dataset-xl-dark.svg"/>
</a>


## Training Configuration

| Setting | Value |
| --- | --- |
| Training steps | 100000 |
| Batch size | 8 |
| Optimizer | adamw |
| Learning rate | 1e-05 |
| Seed | 1000 |
| LeRobot version | 0.7.1 |

---

## How to Get Started with the Model

New to LeRobot? These guides cover the full workflow:

- **[Install LeRobot](https://huggingface.co/docs/lerobot/main/en/installation)** — set up the `lerobot` package.
- **[Hardware setup](https://huggingface.co/docs/lerobot/main/en/hardware_guide)** — assemble, wire, and calibrate your robot and cameras.
- **[Record data & train a policy](https://huggingface.co/docs/lerobot/en/il_robots)** — the end-to-end imitation-learning walkthrough.
- **[CLI cheat-sheet](https://huggingface.co/docs/lerobot/main/en/cheat-sheet)** — quick reference for the `lerobot-*` commands.

The short version to run and train this policy:

### Run the policy on your robot

```bash
lerobot-rollout \
  --strategy.type=base \
  --robot.type=so_follower \
  --robot.port=<your_robot_port> \
  --robot.cameras="{ <camera_1>: {type: opencv, index_or_path: <index_or_path>, width: 640, height: 480, fps: 30}, <camera_2>: {type: opencv, index_or_path: <index_or_path>, width: 640, height: 480, fps: 30}}" \
  --policy.path=ottery/act_task1 \
  --task="pick up the object" \
  --duration=60
```

Replace the remaining `<...>` placeholders with your own values: `--robot.port` and the camera names/indices are specific to your machine, and the camera names must match the observation keys this policy was trained on.

When `--strategy.type=base` is used the script doesn't record the episodes. Skipping duration will make the policy run indefinitely. For more information look at [rollout documentation](https://huggingface.co/docs/lerobot/main/en/inference).

### Train your own policy

```bash
lerobot-train \
  --dataset.repo_id=${HF_USER}/<dataset> \
  --policy.type=act \
  --output_dir=outputs/train/<policy_repo_id> \
  --job_name=lerobot_training \
  --policy.device=cuda \
  --policy.repo_id=${HF_USER}/<policy_repo_id> \
  --trackio.enable=true
```

_Writes checkpoints to `outputs/train/<policy_repo_id>/checkpoints/`._

---

## Evaluation

<!-- Report real-robot results here: run the policy several times per task and count the
successes. Delete the "No evaluation results" line and fill in this table instead:

| Task | Trials | Successes | Success rate |
| ---- | ------ | --------- | ------------ |
| pick the lego brick | 10 | 8 | 80% |

Also worth noting: anything that affects difficulty (new object positions, lighting,
distractors, a different robot of the same type, ...).
-->

_No evaluation results have been provided for this policy yet._

---

## Citation

If you use this policy, please cite the method linked in the description above, along with LeRobot:

```bibtex
@misc{cadene2024lerobot,
    author = {Cadene, Remi and Alibert, Simon and Soare, Alexander and Gallouedec, Quentin and Zouitine, Adil and Palma, Steven and Kooijmans, Pepijn and Aractingi, Michel and Shukor, Mustafa and Aubakirova, Dana and Russi, Martino and Capuano, Francesco and Pascal, Caroline and Choghari, Jade and Moss, Jess and Wolf, Thomas},
    title = {LeRobot: State-of-the-art Machine Learning for Real-World Robotics in Pytorch},
    howpublished = "\url{https://github.com/huggingface/lerobot}",
    year = {2024}
}
```