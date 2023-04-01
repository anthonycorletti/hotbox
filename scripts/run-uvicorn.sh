#!/bin/sh -x

uvicorn hotbox.api:api ${@}
