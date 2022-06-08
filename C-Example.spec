# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


SETUP_DIR ='E:/Project/Python/Compiler/'


a = Analysis(['Assem_Code.py', 'assem_code_UI.py', 'Auto_lanaly.py', 'DFA.py', 'Grammar_Analysis.py', 'inter.py', 'LL1_UI.py',
					'C-Example.py', 'Mid_code_UI.py', 'min_DFA.py', 'NFA.py', 'NFA2.py', 'op_first.py', 'other_function.py',
					'Result_Deal.py', 'Semantic_Analysis.py', 'Semantic_Identity.py', 'stack.py', 's_quene.py', 'Word_Analysis.py'],
             pathex=['E:/Project/Python/Compiler'],
             binaries=[],
             datas=[(SETUP_DIR + 'Data', 'Data'), (SETUP_DIR + 'Debug', 'Debug'), (SETUP_DIR + 'Img', 'Img'), (SETUP_DIR + 'Test', 'Test'), (SETUP_DIR + 'Data/Grammar', 'Data/Grammar')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='C-Example',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='C-Example',
			   icon='E:/Project/Python/Compiler/Img/logo.ico')
