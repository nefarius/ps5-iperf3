/*
 * Capability selection for iperf 3.22 on Prosper0GDK.
 * The vendored configure script is not run against the PS5 toolchain.
 * Optional facilities are enabled only when the SDK headers and libc
 * expose the corresponding FreeBSD-compatible interface.
 */
#ifndef IPERF_CONFIG_H
#define IPERF_CONFIG_H

#define HAVE_CLOCK_GETTIME 1
#define HAVE_CLOCK_NANOSLEEP 1
#define HAVE_CPUSET_SETAFFINITY 1
#define HAVE_CPU_AFFINITY 1
#define HAVE_DAEMON 1
#define HAVE_DLFCN_H 1
#define HAVE_DONT_FRAGMENT 1
#define HAVE_INTTYPES_H 1
#define HAVE_IP_DONTFRAG 1
#define HAVE_MSG_TRUNC 1
#define HAVE_NANOSLEEP 1
#define HAVE_POLL_H 1
#define HAVE_PTHREAD 1
#define HAVE_PTHREAD_PRIO_INHERIT 1
#define HAVE_SENDFILE 1
#define HAVE_SOCKET_SHUTDOWN_SHUT_WR 1
#define HAVE_STDATOMIC_H 1
#define HAVE_STDINT_H 1
#define HAVE_STDIO_H 1
#define HAVE_STDLIB_H 1
#define HAVE_STRINGS_H 1
#define HAVE_STRING_H 1
#define HAVE_SYS_ENDIAN_H 1
#define HAVE_SYS_SOCKET_H 1
#define HAVE_SYS_STAT_H 1
#define HAVE_SYS_TYPES_H 1
#define HAVE_TCP_CONGESTION 1
#define HAVE_TCP_INFO_SND_WND 1
#define HAVE_TCP_KEEPALIVE 1
#define HAVE_UNISTD_H 1

#define PACKAGE_NAME "iperf"
#define PACKAGE_TARNAME "iperf"
#define PACKAGE_VERSION "3.22"
#define PACKAGE_STRING "iperf 3.22"
#define PACKAGE_BUGREPORT "https://github.com/esnet/iperf"
#define PACKAGE_URL "https://software.es.net/iperf/"
#define VERSION "3.22"
#define STDC_HEADERS 1

#endif
