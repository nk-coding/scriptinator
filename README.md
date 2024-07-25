# Scriptinator

Generate your script based on a `config.yaml`

Requires docker.

Example config:
```yaml
files:
  - file: "Intro.pdf"
    title: Intro
    format: 1x3
    slides: [1, 2, 3, 4, 5]
  - file: "Languages.pdf"
    title: Languages
    format: 1x3
    slides: [1, 2, 3]
```
Input files should be in directory `input`

Generate your pdf using
```bash
./run.sh
```