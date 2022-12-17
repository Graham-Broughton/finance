/* -*- Mode: C; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */

/*  Fluent Bit
 *  ==========
 *  Copyright (C) 2015-2022 The Fluent Bit Authors
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

#ifndef FLB_INFO_H
#define FLB_INFO_H

#define STR_HELPER(s)      #s
#define STR(s)             STR_HELPER(s)

#define FLB_SOURCE_DIR "C:/projects/fluent-bit-2e87g"

/* General flags set by CMakeLists.txt */
#ifndef FLB_HAVE_IN_STORAGE_BACKLOG
#define FLB_HAVE_IN_STORAGE_BACKLOG
#endif
#ifndef FLB_HAVE_PARSER
#define FLB_HAVE_PARSER
#endif
#ifndef FLB_HAVE_RECORD_ACCESSOR
#define FLB_HAVE_RECORD_ACCESSOR
#endif
#ifndef FLB_HAVE_STREAM_PROCESSOR
#define FLB_HAVE_STREAM_PROCESSOR
#endif
#ifndef JSMN_PARENT_LINKS
#define JSMN_PARENT_LINKS
#endif
#ifndef JSMN_STRICT
#define JSMN_STRICT
#endif
#ifndef FLB_HAVE_TLS
#define FLB_HAVE_TLS
#endif
#ifndef FLB_HAVE_OPENSSL
#define FLB_HAVE_OPENSSL
#endif
#ifndef FLB_HAVE_METRICS
#define FLB_HAVE_METRICS
#endif
#ifndef FLB_HAVE_AWS
#define FLB_HAVE_AWS
#endif
#ifndef FLB_HAVE_SIGNV4
#define FLB_HAVE_SIGNV4
#endif
#ifndef FLB_HAVE_SQLDB
#define FLB_HAVE_SQLDB
#endif
#ifndef FLB_HAVE_METRICS
#define FLB_HAVE_METRICS
#endif
#ifndef FLB_HAVE_HTTP_SERVER
#define FLB_HAVE_HTTP_SERVER
#endif
#ifndef FLB_HAVE_TIMESPEC_GET
#define FLB_HAVE_TIMESPEC_GET
#endif
#ifndef FLB_MSGPACK_TO_JSON_INIT_BUFFER_SIZE
#define FLB_MSGPACK_TO_JSON_INIT_BUFFER_SIZE "2.0"
#endif
#ifndef FLB_MSGPACK_TO_JSON_REALLOC_BUFFER_SIZE
#define FLB_MSGPACK_TO_JSON_REALLOC_BUFFER_SIZE "0.10"
#endif
#ifndef FLB_HAVE_PROXY_GO
#define FLB_HAVE_PROXY_GO
#endif
#ifndef FLB_HAVE_REGEX
#define FLB_HAVE_REGEX
#endif
#ifndef ONIG_EXTERN
#define ONIG_EXTERN "extern"
#endif
#ifndef FLB_HAVE_UTF8_ENCODER
#define FLB_HAVE_UTF8_ENCODER
#endif
#ifndef FLB_HAVE_LUAJIT
#define FLB_HAVE_LUAJIT
#endif


#define FLB_INFO_FLAGS " FLB_HAVE_IN_STORAGE_BACKLOG FLB_HAVE_PARSER FLB_HAVE_RECORD_ACCESSOR FLB_HAVE_STREAM_PROCESSOR JSMN_PARENT_LINKS JSMN_STRICT FLB_HAVE_TLS FLB_HAVE_OPENSSL FLB_HAVE_METRICS FLB_HAVE_AWS FLB_HAVE_SIGNV4 FLB_HAVE_SQLDB FLB_HAVE_METRICS FLB_HAVE_HTTP_SERVER FLB_HAVE_TIMESPEC_GET FLB_HAVE_PROXY_GO FLB_HAVE_REGEX FLB_HAVE_UTF8_ENCODER FLB_HAVE_LUAJIT"
#endif
