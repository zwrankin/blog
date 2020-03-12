# Welcome to the Blog of Zane Rankin
Various passion projects for personal learning, published (sometimes) to https://zwrankin.github.io  
The README of each subdirectory will provide blog post specific information.   
Note that a few posts merited their own repositories, including 
- https://github.com/zwrankin/health_indicators


# Reproducibility/ Running yourself!
There are two ways to run these analyses.   
NOTE - at the moment these analysis are not pinned to specific images. As per the Kaggle [docs](https://www.kaggle.com/docs/kernels#dockerfiles-and-kernel-versions), "Even if you are using one of the default Kaggle containers, the number, names, and versions of the packages that you’re using are still a moving target."
## Locally - Fork/Clone this repo and run the notebooks in a Docker container
Kaggle has an excellent post about [How to Get Started with Data Science in Containers](https://medium.com/@kaggleteam/how-to-get-started-with-data-science-in-containers-6ed48cb08266). This includes information on how to download Kaggle's Docker Image. In short, the steps (assuming you have the Docker daemon installed and running) for linux/mac are: 
1) Pull the latest image `docker pull kaggle/python` (warning - the image is ~18GB)
2) Add helpful bash functions to your `bashrc`
```
echo '''
kjupyter() {
    docker run -v $PWD:/tmp/working -w=/tmp/working -p 8888:8888 --rm -it kaggle/python bash -c "jupyter notebook --notebook-dir=/tmp/working --ip='*' --port=8888 --no-browser --allow-root"
}
''' >> ~/.bashrc && source ~/.bashrc
```
3) Run `kpython` to launch the notebook and navigate to `http://localhost:8888/` in your browser. Note that as is, you must be in the blog-level directory (e.g. `blog/tree_canopy_cover`).  

## On Kaggle's managed services
Kaggle provides a streamlined and **free** tech stack for pet projects. This combines the storage of [Kaggle Datasets](https://www.kaggle.com/docs/datasets) with the computing of [Kaggle Kernels](https://www.kaggle.com/docs/kernels) (which use the same Docker images as above).  
For example, for the Tree Canopy Cover analysis, I saved the dataset and kernel to https://www.kaggle.com/zwrankin/usfs-tree-canopy-cover. 

