
from PIL import Image
import sys
import random
import argparse
import threading


lock = threading.Lock()

def color_diff(a, b):
	d0 = a[0]-b[0]
	d1 = a[1]-b[1]
	d2 = a[2]-b[2]
	d0 = d0 if d0>0 else d0*-1
	d1 = d1 if d1>0 else d1*-1
	d2 = d2 if d2>0 else d2*-1
	return d0+d1+d2

def med(cluster, k):
	if(len(cluster) == 0):
		return k
	r,g,b = (0,0,0)
	for c in cluster:
		r = r + c[0]
		g = g + c[1]
		b = b + c[2]
	r = r/len(cluster)
	g = g/len(cluster)
	b = b/len(cluster)
	return [r,g,b]

def calc_thread(image, k, cluster, width, height, k_len, offset):
	minimum = len(k)
	for i in range(offset, offset+width):
		for j in range(0, height):
			minimum = len(k)
			difference = 766
			for l in range(0, len(k)):
				new_diff = color_diff(image.getpixel((i, j)), k[l])
				if(new_diff < difference):
					difference = new_diff
					minimum = l
			lock.acquire()
			cluster[minimum].append(image.getpixel((i, j)))
			lock.release()



def assign_cluster_t(im, k, cluster, width, height, k_len, t_num):
	tl = []
	for i in range(0, t_num):
		t = threading.Thread(target=calc_thread, args=(im, k, cluster, int(round(width/t_num)), height, k_len, i*int(round(width/t_num)),))
		tl.append(t)
	for t in tl:
		t.start()
	for t in tl:
		t.join()


def assign_cluster(im, k, cluster, width, height, k_len):
	minimum = len(k)
	for i in range(0, width):
		for j in range(0, height):
			minimum = len(k)
			difference = 766
			for l in range(0, len(k)):
				new_diff = color_diff(im.getpixel((i, j)), k[l])
				if(new_diff < difference):
					difference = new_diff
					minimum = l
			cluster[minimum].append(im.getpixel((i, j)))

def med_ks(k, cluster):
	for i in range(0, len(k)):
		k[i] = med(cluster[i], k[i])

def kmeans(im, k_len, t):
	width, height = im.size
	k = []
	cluster = []
	cluster1 = []
	cluster2 = []
	cluster3 = []
	for i in range(0,k_len):
		k.append(im.getpixel((random.randint(0,width), random.randint(0,height))))
		cluster.append([])
		cluster1.append([])
		cluster2.append([])
		cluster3.append([])
	print(k)
	assign_cluster_t(im, k, cluster, width, height, k_len, t)
	med_ks(k, cluster)
	print(k)
	assign_cluster_t(im, k, cluster1, width, height, k_len, t)
	med_ks(k, cluster1)
	print(k)
	assign_cluster_t(im, k, cluster2, width, height, k_len, t)
	med_ks(k, cluster2)
	print(k)
	assign_cluster_t(im, k, cluster3, width, height, k_len, t)
	med_ks(k, cluster3)
	print(k)
	return k



def main():
	parser = argparse.ArgumentParser(description='Find main colors in a given image.')
	parser.add_argument("image", help="Image to be processed")
	parser.add_argument("-k",type=int, help="Custom K for KMeans algorithm", default=3)
	parser.add_argument('--fast', action='store_true', help="Activate fast mode")
	parser.add_argument("-t",type=int, help="Number of threads to use for computation",default=1)
	parser.add_argument("--output-format",type=str, choices=['image-palette','silhouette', 'html-color-code'], help="Output-format", default="html-color-code")
	args = parser.parse_args()
	print(args)
	print("pirveli argumenti:" + args.k)
	print("meore argumenti:" + args.t)
	image = Image.open(args.image)
	if(args.fast):
		im = image.copy()
		im.thumbnail((int(image.size[0]/10),int(image.size[1]/10)))
		k = kmeans(im, args.k, args.t)
	else:
		k = kmeans(image, args.k, args.t)
	if(args.output_format == "image-palette"):
		img = Image.new('RGB', (image.size[0]+100, image.size[1]))
		img.paste(image)
		imgs = []
		for k_i in range(0, args.k):
			imgs.append(Image.new('RGB', (100, image.size[1]/args.k), color = tuple(k[k_i])))
		for k_i in range(0, args.k):
			img.paste(imgs[k_i], box=(image.size[0], k_i*(image.size[1]/args.k)))
		img.save(args.image +"_pallette.png", "PNG")	
	elif(args.output_format == "silhouette"):
		img = Image.new('RGB', (image.size[0], image.size[1]))
		for x in range(0, img.size[0]):
			for y in range(0, img.size[1]):
				minimum = len(k)
				difference = 766
				for l in range(0, len(k)):
					new_diff = color_diff(image.getpixel((x, y)), k[l])
					if(new_diff < difference):
						difference = new_diff
						minimum = l
				img.putpixel((x,y), tuple(k[minimum]))
		img.save(args.image +"_silhouette.png", "PNG")
	else:
		for k_i in k:
			print("#%02x%02x%02x" % (k_i[0],k_i[1],k_i[2]))


if __name__ == "__main__":
	main()