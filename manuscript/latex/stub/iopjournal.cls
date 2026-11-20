% Minimal stand-in for IOP Publishing's iopjournal.cls, for local test builds only.
% Use the real class (IOP Publishing LaTeX template) for submission.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{iopjournal}[2026/11/20 local stand-in]
\LoadClass[11pt,a4paper]{article}
\RequirePackage{graphicx,fancyhdr,xcolor,hyperref}
\RequirePackage[margin=25mm]{geometry}
\newcommand{\articletype}[1]{\def\@articletype{#1}}
\newcommand{\affil}[1]{\g@addto@macro\@affils{\par{\small #1}}}
\def\@affils{}
\newcommand{\email}[1]{\g@addto@macro\@affils{\par{\small E-mail: #1}}}
\newcommand{\keywords}[1]{\def\@kw{#1}}\def\@kw{}
\newcommand{\orcid}[1]{}
\renewcommand{\maketitle}{}
\renewenvironment{abstract}{\begin{center}{\Large\bfseries\@title\par}\medskip\@author\par\@affils\par\end{center}\noindent\textbf{Abstract.}\ }{\par\noindent\textbf{Keywords:} \@kw\par\bigskip}
\newcommand{\ack}[1]{\section*{Acknowledgments}#1}
\newcommand{\funding}[1]{\section*{Funding}#1}
\newcommand{\roles}[1]{\section*{Roles}#1}
\newcommand{\data}[1]{\section*{Data availability statement}#1}
\newcommand{\suppdata}[1]{\section*{Supplementary data}#1}
\endinput
