# brave/container.py
from dependency_injector import containers, providers
from brave.app_manager import AppManager
from fastapi import FastAPI

class AppContainer(containers.DeclarativeContainer):
    app_manager = providers.Singleton(AppManager, app=providers.Dependency(instance_of=FastAPI))
