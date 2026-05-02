// 0x100e89b90 @ 0x100e89b90
__int64 __fastcall send_tunnel_add_link(unsigned __int16 *a1, unsigned __int16 *a2)
{
  __int64 type; // rsi
  __int64 v3; // rdx
  __int64 v4; // rcx
  __int64 v5; // r8
  __int64 v6; // r9
  int fd_session_log_print_info; // eax
  __int64 v8; // rdi
  __int64 v9; // rdx
  __int64 v10; // r8
  __int64 v11; // r9
  int v12; // eax
  __int64 v13; // rax
  __int64 v14; // rdx
  __int64 v15; // rcx
  __int64 v16; // r8
  __int64 v17; // r9
  __int64 v18; // rsi
  __int64 v19; // rdx
  __int64 v20; // rcx
  __int64 v21; // r8
  __int64 v22; // r9
  __int64 v23; // rdi
  __int64 v24; // rdx
  __int64 v25; // rcx
  __int64 v26; // r8
  __int64 v27; // r9
  __int64 v28; // rdx
  __int64 v29; // rcx
  __int64 v30; // r8
  __int64 v31; // r9
  __int64 v32; // rdx
  __int64 v33; // rcx
  __int64 v34; // r8
  __int64 v35; // r9
  __int64 v36; // rsi
  __int64 v37; // rdx
  __int64 v38; // r8
  __int64 v39; // r9
  __int64 v40; // rcx
  __int64 v41; // rsi
  __int64 v42; // rdx
  __int64 v43; // rdx
  __int64 v44; // rcx
  __int64 v45; // r8
  __int64 v46; // r9
  __int64 v47; // rcx
  char *v48; // rdi
  __int64 v49; // rdx
  __int64 v50; // rcx
  __int64 v51; // r8
  __int64 v52; // r9
  unsigned __int16 *v53; // rdi
  __int64 v54; // rdx
  __int64 v55; // rcx
  __int64 v56; // r8
  __int64 v57; // r9
  unsigned __int16 *v58; // rdi
  __int64 v59; // rsi
  __int64 v60; // rdx
  __int64 v61; // rcx
  __int64 v62; // r8
  __int64 v63; // r9
  char *v64; // rdi
  __int64 v65; // rsi
  __int64 v66; // rdx
  __int64 v67; // rcx
  __int64 v68; // r8
  __int64 v69; // r9
  int v70; // eax
  unsigned __int16 *v71; // rdi
  __int64 v72; // rdx
  __int64 v73; // rcx
  __int64 v74; // r8
  __int64 v75; // r9
  int v76; // eax
  __int64 v78; // [rsp+0h] [rbp-170h]
  __int64 v79; // [rsp+8h] [rbp-168h]
  __int64 v80; // [rsp+78h] [rbp-F8h]
  int v81; // [rsp+90h] [rbp-E0h] BYREF
  unsigned int v82; // [rsp+94h] [rbp-DCh]
  unsigned int v83; // [rsp+98h] [rbp-D8h]
  int v84; // [rsp+9Ch] [rbp-D4h] BYREF
  unsigned __int16 *v85; // [rsp+A0h] [rbp-D0h]
  unsigned __int8 v86; // [rsp+AFh] [rbp-C1h]
  __int64 v87; // [rsp+B0h] [rbp-C0h]
  unsigned __int16 *v88; // [rsp+B8h] [rbp-B8h]
  unsigned __int16 *v89; // [rsp+C0h] [rbp-B0h]
  char v91[16]; // [rsp+D0h] [rbp-A0h] BYREF
  _BYTE __b[128]; // [rsp+E0h] [rbp-90h] BYREF

  v89 = a1; /*0x100e89bac*/
  v88 = a2; /*0x100e89bb3*/
  memset(__b, 0, sizeof(__b)); /*0x100e89bd1*/
  memset(v91, 0, sizeof(v91)); /*0x100e89beb*/
  v80 = *((_QWORD *)a1 + 33); /*0x100e89bfe*/
  type = spice_session_get_type(); /*0x100e89c11*/
  v87 = g_type_instance_get_private(v80, type); /*0x100e89c19*/
  if ( (unsigned int)spice_util_get_debug(v80, type, v3, v4, v5, v6) && spice_gtk_log_level < 1 ) /*0x100e89c38*/
  {
    fd_session_log_print_info = get_fd_session_log_print_info(v89, __b, 128); /*0x100e89c51*/
    type = 128; /*0x100e89c5d*/
    g_log( /*0x100e89c7b*/
      (unsigned int)"GSpice",
      128,
      (unsigned int)"[%-38s:%4d] Initiating tunnel add link process for session %s",
      (unsigned int)"send_tunnel_add_link",
      4836,
      fd_session_log_print_info);
  }
  v8 = *((_QWORD *)v89 + 33); /*0x100e89c8c*/
  v86 = sub_100E8A910(v8); /*0x100e89c98*/
  if ( v86 )
  {
    if ( (unsigned int)spice_util_get_debug(v8, type, v9, v86, v10, v11) && spice_gtk_log_level < 2 ) /*0x100e89d47*/
    {
      v13 = get_fd_session_log_print_info(v89, __b, 128); /*0x100e89d6f*/
      g_log( /*0x100e89da1*/
        (unsigned int)"GSpice",
        64,
        (unsigned int)"[%-38s:%4d] Allocated virtual channel ID %u for session %s",
        (unsigned int)"send_tunnel_add_link",
        4844,
        v86,
        v13);
    }
    v85 = (unsigned __int16 *)g_malloc0_n(1, 168); /*0x100e89dba*/
    if ( v85 )
    {
      if ( (unsigned int)spice_util_get_debug(1, 168, v14, v15, v16, v17) && spice_gtk_log_level < 1 ) /*0x100e89e55*/
        g_log( /*0x100e89e85*/
          (unsigned int)"GSpice",
          128,
          (unsigned int)"[%-38s:%4d] Created proxy channel management structure for virtual channel ID %u",
          (unsigned int)"send_tunnel_add_link",
          4853,
          v86);
      v18 = *((unsigned __int8 *)v88 + 2); /*0x100e89e9d*/
      sub_100E8AAC0(v89, v18); /*0x100e89ea1*/
      if ( (unsigned int)spice_util_get_debug(v89, v18, v19, v20, v21, v22) && spice_gtk_log_level < 1 ) /*0x100e89ebe*/
      {
        LODWORD(v78) = v86; /*0x100e89f07*/
        g_log( /*0x100e89f0d*/
          (unsigned int)"GSpice",
          128,
          (unsigned int)"[%-38s:%4d] Set session priority to %d for virtual channel ID %u",
          (unsigned int)"send_tunnel_add_link",
          4857,
          *((unsigned __int8 *)v88 + 2),
          v78);
      }
      *((_BYTE *)v89 + 69300) = v86; /*0x100e89f26*/
      *v85 = v86; /*0x100e89f3a*/
      *((_DWORD *)v85 + 41) = 0; /*0x100e89f44*/
      *((_DWORD *)v85 + 39) = *((_DWORD *)v89 + 6); /*0x100e89f5f*/
      v85[80] = v88[77]; /*0x100e89f7a*/
      if ( *((_DWORD *)v88 + 1) ) /*0x100e89f88*/
      {
        *(_DWORD *)(v85 + 3) = *((_DWORD *)v88 + 1); /*0x100e8a030*/
        v84 = sub_100E8AB50(*((unsigned int *)v88 + 1)); /*0x100e8a055*/
        v23 = 2; /*0x100e8a062*/
        inet_ntop(2, &v84, v91, 0x10u); /*0x100e8a06f*/
        if ( (unsigned int)spice_util_get_debug(2, &v84, v32, v33, v34, v35) && spice_gtk_log_level < 1 ) /*0x100e8a08c*/
        {
          v23 = (__int64)"GSpice"; /*0x100e8a0a0*/
          LODWORD(v78) = v86; /*0x100e8a0c0*/
          g_log( /*0x100e8a0c5*/
            (unsigned int)"GSpice",
            128,
            (unsigned int)"[%-38s:%4d] Configured IPv4 destination %s for virtual channel ID %u",
            (unsigned int)"send_tunnel_add_link",
            4881,
            (unsigned int)v91,
            v78);
        }
      }
      else
      {
        v23 = (__int64)(v85 + 5); /*0x100e89fb2*/
        ZXMemcpy(v85 + 5, 16, v88 + 4, 16); /*0x100e89fc3*/
        if ( (unsigned int)spice_util_get_debug(v85 + 5, 16, v24, v25, v26, v27) && spice_gtk_log_level < 1 ) /*0x100e89fe0*/
        {
          v23 = (__int64)"GSpice"; /*0x100e89fee*/
          g_log( /*0x100e8a010*/
            (unsigned int)"GSpice",
            128,
            (unsigned int)"[%-38s:%4d] Configured IPv6 destination for virtual channel ID %u",
            (unsigned int)"send_tunnel_add_link",
            4876,
            v86);
        }
      }
      LOWORD(v29) = *v88; /*0x100e8a0db*/
      v85[1] = *v88; /*0x100e8a0e5*/
      *((_BYTE *)v85 + 4) = *((_BYTE *)v88 + 2); /*0x100e8a0fa*/
      LOBYTE(v28) = *((_BYTE *)v88 + 3); /*0x100e8a104*/
      *((_BYTE *)v85 + 5) = v28; /*0x100e8a10e*/
      v83 = ((int)v88[77] >> 8) & 0x7F; /*0x100e8a125*/
      v36 = (unsigned __int8)v88[77]; /*0x100e8a139*/
      v82 = (unsigned __int8)v88[77]; /*0x100e8a13f*/
      if ( (unsigned int)spice_util_get_debug(v23, v36, v28, v29, v30, v31) && spice_gtk_log_level < 1 ) /*0x100e8a15d*/
      {
        v23 = (__int64)"GSpice"; /*0x100e8a17e*/
        v36 = 128; /*0x100e8a185*/
        LODWORD(v78) = v82; /*0x100e8a1a7*/
        g_log( /*0x100e8a1b6*/
          (unsigned int)"GSpice",
          128,
          (unsigned int)"[%-38s:%4d] Extracted channel type %d and channel ID %d from combined field 0x%X",
          (unsigned int)"send_tunnel_add_link",
          4892,
          v83,
          v78,
          v88[77]);
      }
      v40 = v89[198]; /*0x100e8a1c7*/
      if ( (_DWORD)v40 == 1 ) /*0x100e8a1d1*/
      {
        LODWORD(v40) = *((unsigned __int8 *)v88 + 83); /*0x100e8a1de*/
        *((_BYTE *)v85 + 85) = v40; /*0x100e8a1e8*/
        *((_DWORD *)v89 + 12) = v88[77]; /*0x100e8a200*/
        v41 = (unsigned __int8)v83; /*0x100e8a219*/
        *((_DWORD *)v88 + 21) = (unsigned __int8)v83 | *((_DWORD *)v88 + 21) & 0xFFFFFF00; /*0x100e8a228*/
        v42 = *((unsigned int *)v88 + 21); /*0x100e8a232*/
        *(_DWORD *)(v85 + 43) = v42; /*0x100e8a23c*/
        if ( (unsigned int)spice_util_get_debug(v23, v41, v42, v40, v38, v39) && spice_gtk_log_level < 2 ) /*0x100e8a257*/
        {
          v23 = (__int64)"GSpice"; /*0x100e8a26f*/
          v41 = 64; /*0x100e8a276*/
          LODWORD(v78) = *((_DWORD *)v88 + 21); /*0x100e8a29f*/
          g_log( /*0x100e8a2a5*/
            (unsigned int)"GSpice",
            64,
            (unsigned int)"[%-38s:%4d] Configuring SPICE link type for virtual channel ID %u, link info channel type %u",
            (unsigned int)"send_tunnel_add_link",
            4899,
            v86,
            v78);
        }
        if ( v83 == 10 ) /*0x100e8a2b6*/
        {
          if ( (unsigned int)spice_util_get_debug(v23, v41, v43, v44, v45, v46) && spice_gtk_log_level < 2 ) /*0x100e8a2d9*/
          {
            LODWORD(v78) = v82; /*0x100e8a30d*/
            g_log( /*0x100e8a312*/
              (unsigned int)"GSpice",
              64,
              (unsigned int)"[%-38s:%4d] Configuring port channel for virtual channel ID %u with port channel ID %d",
              (unsigned int)"send_tunnel_add_link",
              4902,
              v86,
              v78);
          }
          *((_DWORD *)v89 + 14) = 1; /*0x100e8a323*/
          *((_DWORD *)v89 + 15) = v82; /*0x100e8a337*/
        }
      }
      else
      {
        *((_DWORD *)v88 + 21) = *((_DWORD *)v88 + 21) & 0xFFFFFF00 | 0xC; /*0x100e8a359*/
        v47 = *((unsigned int *)v88 + 21); /*0x100e8a363*/
        *(_DWORD *)(v85 + 43) = v47; /*0x100e8a36d*/
        if ( (unsigned int)spice_util_get_debug(v23, v36, v37, v47, v38, v39) && spice_gtk_log_level < 2 ) /*0x100e8a388*/
        {
          LODWORD(v78) = *((_DWORD *)v88 + 21); /*0x100e8a3d0*/
          g_log( /*0x100e8a3d6*/
            (unsigned int)"GSpice",
            64,
            (unsigned int)"[%-38s:%4d] Configuring non-SPICE link type for virtual channel ID %u, link info channel type "
                          "%u, using outband channel type",
            (unsigned int)"send_tunnel_add_link",
            4910,
            v86,
            v78);
        }
      }
      ZXStrncopy(v85 + 53, 33, v88 + 52, 32); /*0x100e8a416*/
      v48 = (char *)v85 + 139; /*0x100e8a43e*/
      ZXStrncopy((char *)v85 + 139, 17, (char *)v88 + 137, 16); /*0x100e8a452*/
      if ( (unsigned int)spice_util_get_debug(v48, 17, v49, v50, v51, v52) && spice_gtk_log_level < 1 ) /*0x100e8a46f*/
        g_log( /*0x100e8a49f*/
          (unsigned int)"GSpice",
          128,
          (unsigned int)"[%-38s:%4d] Copied OpenTelemetry trace information for virtual channel ID %u",
          (unsigned int)"send_tunnel_add_link",
          4915,
          v86);
      v53 = v89; /*0x100e8a4a9*/
      sub_100E8AB60(v89, v83, v82); /*0x100e8a4bc*/
      if ( (unsigned int)spice_util_get_debug(v53, v83, v54, v55, v56, v57) && spice_gtk_log_level < 1 )
      {
        LODWORD(v78) = v83; /*0x100e8a51c*/
        LODWORD(v79) = v82; /*0x100e8a525*/
        g_log(
          (unsigned int)"GSpice",
          128,
          (unsigned int)"[%-38s:%4d] Configured bandwidth control for virtual channel ID %u (type: %d, ID: %d)",
          (unsigned int)"send_tunnel_add_link",
          4919,
          v86,
          v78,
          v79);
      }
      sub_100E8ADE0(v88); /*0x100e8a53c*/
      v58 = v89; /*0x100e8a541*/
      v59 = v86; /*0x100e8a548*/
      if ( (unsigned int)sub_100E8AF80(v89, v86, v85 + 1) )
      {
        *((_BYTE *)v89 + 132) = 1; /*0x100e8a578*/
        opentelemetry_redirect_processtrack_end(v89 + 34036, 1, 0); /*0x100e8a598*/
        g_rw_lock_writer_lock(v87 + 5032); /*0x100e8a5ae*/
        g_hash_table_insert(*(_QWORD *)(v87 + 5048), *v85, v85); /*0x100e8a5d7*/
        g_rw_lock_writer_unlock(v87 + 5032); /*0x100e8a5f3*/
        if ( *((_DWORD *)v88 + 1) ) /*0x100e8a5ff*/
        {
          v81 = sub_100E8AB50(*((unsigned int *)v88 + 1)); /*0x100e8a62b*/
          v64 = (char *)2; /*0x100e8a638*/
          v65 = (__int64)&v81; /*0x100e8a63d*/
          inet_ntop(2, &v81, v91, 0x10u); /*0x100e8a645*/
        }
        else
        {
          v64 = v91; /*0x100e8a64f*/
          v65 = (__int64)"[IPv6]"; /*0x100e8a656*/
          if ( (unsigned __int64)g_strlcpy(v91, "[IPv6]", 16) >= 0x10 ) /*0x100e8a676*/
          {
            if ( (unsigned int)spice_util_get_debug(v91, "[IPv6]", v66, v67, v68, v69) && spice_gtk_log_level < 3 ) /*0x100e8a699*/
            {
              v64 = "GSpice"; /*0x100e8a6a7*/
              v65 = 16; /*0x100e8a6ae*/
              g_log( /*0x100e8a6c9*/
                (unsigned int)"GSpice",
                16,
                (unsigned int)"[%-38s:%4d] IPv6 label truncated during string copy for virtual channel ID %u",
                (unsigned int)"send_tunnel_add_link",
                4938,
                v86);
            }
            v91[15] = 0; /*0x100e8a6d3*/
          }
        }
        if ( (unsigned int)spice_util_get_debug(v64, v65, v66, v67, v68, v69) && spice_gtk_log_level < 2 )
        {
          v70 = get_fd_session_log_print_info(v89, __b, 128); /*0x100e8a715*/
          LODWORD(v79) = *v88; /*0x100e8a79b*/
          g_log(
            (unsigned int)"GSpice",
            64,
            (unsigned int)"[%-38s:%4d] Successfully established tunnel link for session %s: destination %s:%d, channel ty"
                          "pe %d, channel ID %d -> virtual channel ID %u",
            (unsigned int)"send_tunnel_add_link",
            4943,
            v70,
            v91,
            v79,
            v83,
            v82,
            *v85);
        }
        return (unsigned __int8)*v85; /*0x100e8a7ce*/
      }
      else
      {
        if ( (unsigned int)spice_util_get_debug(v58, v59, v60, v61, v62, v63) ) /*0x100e8a7de*/
          g_log( /*0x100e8a816*/
            (unsigned int)"GSpice",
            8,
            (unsigned int)"[%-38s:%4d] Tunnel link message transmission failed for virtual channel ID %u, cleaning up resources",
            (unsigned int)"send_tunnel_add_link",
            4947,
            v86);
        v71 = v89; /*0x100e8a820*/
        set_fd_session_flag(v89, 16, 4948); /*0x100e8a831*/
        if ( v85 ) /*0x100e8a83e*/
        {
          v71 = v85; /*0x100e8a84b*/
          g_free(v85); /*0x100e8a84e*/
          v85 = 0; /*0x100e8a853*/
        }
        if ( (unsigned int)spice_util_get_debug(v71, 16, v72, v73, v74, v75) ) /*0x100e8a868*/
        {
          v76 = get_fd_session_log_print_info(v89, __b, 128); /*0x100e8a889*/
          g_log( /*0x100e8a8b3*/
            (unsigned int)"GSpice",
            8,
            (unsigned int)"[%-38s:%4d] Tunnel add link process failed for session %s",
            (unsigned int)"send_tunnel_add_link",
            4950,
            v76);
        }
        return 0; /*0x100e8a8bd*/
      }
    }
    else
    {
      if ( (unsigned int)spice_util_get_debug(1, 168, v14, v15, v16, v17) ) /*0x100e89dd4*/
        g_log( /*0x100e89e0c*/
          (unsigned int)"GSpice",
          8,
          (unsigned int)"[%-38s:%4d] Memory allocation failed for proxy channel management structure (virtual channel ID %u)",
          (unsigned int)"send_tunnel_add_link",
          4849,
          v86);
      set_fd_session_flag(v89, 16, 4850); /*0x100e89e27*/
      return 0; /*0x100e89e2c*/
    }
  }
  else
  {
    if ( (unsigned int)spice_util_get_debug(v8, type, v9, 0, v10, v11) ) /*0x100e89cb3*/
    {
      v12 = get_fd_session_log_print_info(v89, __b, 128); /*0x100e89cd4*/
      g_log( /*0x100e89cfe*/
        (unsigned int)"GSpice",
        8,
        (unsigned int)"[%-38s:%4d] Failed to allocate virtual channel ID for session %s - no available channels",
        (unsigned int)"send_tunnel_add_link",
        4840,
        v12);
    }
    set_fd_session_flag(v89, 16, 4841); /*0x100e89d19*/
    return 0; /*0x100e89d1e*/
  }
}
