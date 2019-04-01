from conans import ConanFile, CMake, tools


class HmlpConan(ConanFile):
    name = "hmlp"
    version = "0.1"
    license = "GNU GPL"
    author = "xyc chyacinthz@gmail.com"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of hmlp here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "tacc": [True, False],
        "mpi": [True, False],
        "blas": [True, False], 
        "cuda": [True, False]
    }
    default_options = {
        "shared":False,
        "tacc": False,
        "mpi": False,
        "blas": True, 
        "cuda": False
    }
    generators = "cmake"
    script = ''

    def source(self):        
        self.run("git clone https://github.com/ChenhanYu/hmlp.git")
        self.run("cd hmlp && git checkout master")
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        tools.replace_in_file("hmlp/CMakeLists.txt", "PROJECT(hmlp C CXX)",
                              '''PROJECT(hmlp C CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

        self.script = ''

        if self.options.tacc:
            self.script = 'hmlp/set_env_tacc.sh'
        else:
            self.script = 'hmlp/set_env.sh'
        
        if self.options.mpi:
            tools.replace_in_file(self.script, "export HMLP_USE_MPI=false", "export HMLP_USE_MPI=true", strict=False)
        else:
            tools.replace_in_file(self.script, "export HMLP_USE_MPI=true", "export HMLP_USE_MPI=false", strict=False)
        
        if self.options.blas:
            tools.replace_in_file(self.script, "export HMLP_USE_BLAS=false", "export HMLP_USE_BLAS=true", strict=False)
        else:
            tools.replace_in_file(self.script, "export HMLP_USE_BLAS=true", "export HMLP_USE_BLAS=false", strict=False)

        if self.options.cuda:
            tools.replace_in_file(self.script, "export HMLP_USE_CUDA=false", "export HMLP_USE_CUDA=true", strict=False)
        else:
            tools.replace_in_file(self.script, "export HMLP_USE_CUDA=true", "export HMLP_USE_CUDA=false", strict=False)        
        
    def build(self):
        if self.options.tacc:
            script = 'hmlp/set_env_tacc.sh'
        else:
            script = 'hmlp/set_env.sh'
        cmake = CMake(self)
        if (self.settings.os == "Macos"):
            cmake.definitions["BUILD_UNIT_TESTS"] = False
            cmake.definitions["BUILD_MOCK_TESTS"] = False
            self.run('source ' + script + ' && cmake "{}" {}'.format('hmlp', cmake.command_line) + ' && cmake --build .{}'.format(cmake.build_config) + ' && cmake --build . --target install')

        if (self.settings.os == "Linux"):
            self.run('source ' + script + ' && cmake "{}" {}'.format('hmlp', cmake.command_line) + ' && cmake --build .{}'.format(cmake.build_config) + ' && cmake --build . --target install')

        #cmake.configure(source_folder="hello")
        #cmake.build()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src="hmlp")
        self.copy("*.hpp", dst="include", src="hmlp")
        
        self.copy("*hmlp.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs=['/usr/local/include', 'include', 
            'include/gofmm', 'include/include', 'include/frame',
            'include/frame/base', 'include/frame/containers', 'include/frame/external',
            'include/frame/primitives', 'include/frame/pvfmm'
            ]
        self.cpp_info.libdirs = ['/usr/local/lib', 'lib']
        self.cpp_info.cppflags = ["-Xpreprocessor -fopenmp -lomp", "-std=c++11"]
        #self.cpp_info.libs = ["hmlp"]
        print(self.settings.os)
        #if self.settings.os=="Macos":