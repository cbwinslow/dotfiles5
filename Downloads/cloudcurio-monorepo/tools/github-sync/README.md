# CBW GitHub & Dotfiles Reorg Bundle

This bundle contains the core scripts and config templates to:

- Bootstrap dotfiles on a new machine using **yadm** and a GitHub-hosted dotfiles repo.
- Sync all **CloudCurio**-related GitHub repos into `~/dev/cloudcurio`.
- Sync all **OpenDiscourse**-related GitHub repos into `~/dev/opendiscourse`.

## Files

- `bin/dotfiles-bootstrap.sh`  
  Install yadm (if needed), clone `git@github.com:cbwinslow/dotfiles.git`, and apply dotfiles to `$HOME`.

- `bin/cloudcurio-sync.sh`  
  Sync CloudCurio repos based on `~/.config/cloudcurio/cloudcurio-repos.yml`.

- `bin/opendiscourse-sync.sh`  
  Sync OpenDiscourse repos based on `~/.config/opendiscourse/opendiscourse-repos.yml`.

- `config/cloudcurio/cloudcurio-repos.yml`  
  Example YAML file listing CloudCurio repos.

- `config/opendiscourse/opendiscourse-repos.yml`  
  Example YAML file listing OpenDiscourse repos.

## Suggested Layout

Place these in your `.dotbins` or scripts repo, for example:

```text
~/.dotbins/
  bin/
    dotfiles-bootstrap.sh
    cloudcurio-sync.sh
    opendiscourse-sync.sh
  config/
    cloudcurio/
      cloudcurio-repos.yml
    opendiscourse/
      opendiscourse-repos.yml
```

Then ensure `~/.dotbins/bin` is on your `PATH`, or reference scripts directly.

## Basic Usage

### 1. Dotfiles bootstrap

```bash
chmod +x ~/.dotbins/bin/dotfiles-bootstrap.sh
~/.dotbins/bin/dotfiles-bootstrap.sh --verbose
```

This will:
- Install `yadm` if missing.
- Clone your dotfiles repo from GitHub.
- Apply dotfiles into `$HOME` via `yadm checkout`.

### 2. CloudCurio repos

Edit `~/.config/cloudcurio/cloudcurio-repos.yml` to match your current repos, then:

```bash
chmod +x ~/.dotbins/bin/cloudcurio-sync.sh
~/.dotbins/bin/cloudcurio-sync.sh --verbose
```

### 3. OpenDiscourse repos

Edit `~/.config/opendiscourse/opendiscourse-repos.yml`, then:

```bash
chmod +x ~/.dotbins/bin/opendiscourse-sync.sh
~/.dotbins/bin/opendiscourse-sync.sh --verbose
```

Optional flags:

- `--dry-run` : Show what would happen without cloning/pulling.
- `--owner`   : Override GitHub owner/org (default: `cloudcurio` / `opendiscourse`).
- `--dest`    : Override destination root directories.
- `--config`  : Use an alternate YAML config file.

## Aliases (example)

Add to your `.zshrc` (tracked by yadm):

```bash
alias dots-bootstrap="$HOME/.dotbins/bin/dotfiles-bootstrap.sh --verbose"
alias cc-sync="$HOME/.dotbins/bin/cloudcurio-sync.sh --verbose"
alias cc-sync-dry="$HOME/.dotbins/bin/cloudcurio-sync.sh --dry-run --verbose"
alias od-sync="$HOME/.dotbins/bin/opendiscourse-sync.sh --verbose"
alias od-sync-dry="$HOME/.dotbins/bin/opendiscourse-sync.sh --dry-run --verbose"
```

This bundle is designed to be a starting point; extend it as you grow the CloudCurio and OpenDiscourse universes.
