import{_ as l}from"./AppLayout-BZnnFZk-.js";import{c as d,o,w as n,a as t,b as p,F as m,r as c,t as a,d as r}from"./app-DEqib_Tg.js";const g={class:"max-w-5xl mx-auto my-12"},x={class:"grid grid-cols-1 md:grid-cols-2 gap-6 mb-16"},b={class:"text-xl font-semibold text-gray-800 mb-2"},u={class:"text-gray-600"},y=`
import os

from fastapi import FastAPI

from fastapi_view import inertia

app = FastAPI(title="api")
inertia.setup(app, directory="resources/views")

@app.get("/")

@app.get("/")
def index():
    return inertia("Index")

@app.get("/about")
def about():
    return inertia("About")
`,h={__name:"About",setup(f){const i=[{title:"快速整合",desc:"輕鬆整合 FastAPI 後端服務"},{title:"Inertia.js & Vite",desc:"支援 Inertia.js 以及 Vite"}];return(_,s)=>(o(),d(l,null,{body:n(()=>[t("div",g,[s[2]||(s[2]=t("div",{class:"text-center mb-16"},[t("h1",{class:"text-4xl font-bold text-gray-900 mb-4"},"FastAPI Client Library"),t("p",{class:"text-xl text-gray-600"},"強大且易用的 FastAPI 前端整合方案")],-1)),t("div",x,[(o(),p(m,null,c(i,e=>t("div",{key:e.title,class:"bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"},[t("h3",b,a(e.title),1),t("p",u,a(e.desc),1)])),64))]),s[3]||(s[3]=t("div",{class:"bg-white rounded-lg shadow-md p-8 mb-16"},[t("h2",{class:"text-2xl font-bold text-gray-900 mb-4"},"快速開始"),t("div",{class:"bg-gray-800 rounded-lg p-4 mb-4"},[t("code",{class:"text-gray-100"},"pip install fastapi-view")])],-1)),t("div",{class:"bg-gray-900 rounded-b-lg p-4 font-mono text-sm"},[t("pre",{class:"language-python"},[s[0]||(s[0]=r("            ",-1)),t("code",{class:"text-gray-300"},`
              `+a(y)+`
            `),s[1]||(s[1]=r(`
          `,-1))])])])]),_:1}))}};export{h as default};
