from setuptools import find_packages, setup

package_name = 'turtle_script'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='saivenkat',
    maintainer_email='Saivenkatkadavergu@todo.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "draw_circle_node = turtle_script.draw_circle:main",
            "draw_spiral_node = turtle_script.draw_sprial:main",
            "area_service_server_node = turtle_script.area_service_server:main",
            "area_service_client_node = turtle_script.area_service_client:main",
            "polygon_drawer_node = turtle_script.polygon_drawer:main",
            "turtle_spwaner_node = turtle_script.turtle_spwaner:main",
            "turtle_controller_node = turtle_script.turtle_controller:main",
            "turtle_kill_spawner_node = turtle_script.turtle_spawner_kill:main",
            "turtle_follower_node = turtle_script.turtle_controller_follwer:main",
            "turtle_aum_node = turtle_script.aum_draw:main",
            
            

        ],
    },
)
