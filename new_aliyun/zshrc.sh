#@IgnoreInspection BashAddShebang
export EDITOR='vim'


export ZSH=${HOME}/.oh-my-zsh

ZSH_THEME="robbyrussell"

DISABLE_AUTO_UPDATE="true"

plugins=(git)

source ${ZSH}/oh-my-zsh.sh

# pyenv

export PATH=${HOME}/.pyenv/bin:$PATH
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv shell 3.6.1

export PYTHONPATH=.
export PYTHONUNBUFFERED=1

setproxy(){
    export http_proxy=http://local.alihz-proxy.qbtrade.org:3128
    export HTTP_PROXY=http://local.alihz-proxy.qbtrade.org:3128
    export https_proxy=http://local.alihz-proxy.qbtrade.org:3128
    export HTTPS_PROXY=http://local.alihz-proxy.qbtrade.org:3128
}
unsetproxy(){
    unset http_proxy
    unset HTTP_PROXY
    unset https_proxy
    unset HTTPS_PROXY
}

# setproxy

PROMPT='%n%{$fg_bold[green]%}@%{$reset_color%}%m %{$fg_bold[green]%}%p %{$fg[cyan]%}%~ %{$fg_bold[blue]%}$(git_prompt_info)%{$fg_bold[blue]%}%{$fg[cyan]%}>%{$reset_color%} '
ZSH_THEME_GIT_PROMPT_DIRTY="%{$fg[blue]%}) %{$fg[yellow]%}o%{$reset_color%}"


alias dod="docker run -it --rm "

alias kb="/opt/bin/kubectl -s http://kube.alihz.qbtrade.org "

alias doquantlib='docker run -it --rm -e QB_REGION=alihk -v /home/id_rsa_bitbucket:/repo-key qbtrade/python bash -c '\''git clone --depth 1 git@github.com:qbtrade/quantlib.git && cd quantlib && make prod && bash'\'''


if [[ -a ${HOME}/.zshrc.local ]]
then
    source ${HOME}/.zshrc.local
fi



export QB_REGION={{REGION}}
