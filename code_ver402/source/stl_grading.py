import os
import json
import numpy as np
import torch
from pytorch3d.structures import Meshes
from pytorch3d.loss import chamfer_distance, point_mesh_face_distance
from pytorch3d.ops import sample_points_from_meshes
import trimesh

# AAD 구현하기!

# Constants and paths
RESULT_PATH = os.path.join(os.getcwd(), "code_ver4.0.0/paper_testcase/results")
STL_PATH = os.path.join(os.getcwd(), "code_ver4.0.0/paper_testcase/hw2/stl")
ANS_STL_PATH = os.path.join(os.getcwd(), "code_ver4.0.0/paper_testcase/answer/stl/hw2_answer.stl")

def load_stl(file_path, device):
    mesh = trimesh.load_mesh(file_path)
    verts = torch.tensor(mesh.vertices, dtype=torch.float32, device=device)
    faces = torch.tensor(mesh.faces, dtype=torch.int64, device=device)
    return verts, faces

def chamfer_distance_score(verts1, faces1, verts2, faces2, device):
    mesh1 = Meshes(verts=[verts1], faces=[faces1])
    mesh2 = Meshes(verts=[verts2], faces=[faces2])
    
    if mesh1.isempty() or mesh2.isempty():
        print("Warning: Empty mesh detected")
        return float('inf')
    
    try:
        points1 = sample_points_from_meshes(mesh1, num_samples=5000)
        points2 = sample_points_from_meshes(mesh2, num_samples=5000)
        loss, _ = chamfer_distance(points1, points2)
        return loss.item()
    except Exception as e:
        print(f"Error in chamfer_distance_score: {str(e)}")
        return float('inf')

def earth_movers_distance(verts1, verts2):
    from geomloss import SamplesLoss
    loss = SamplesLoss(loss="sinkhorn", p=2, blur=0.01)
    return loss(verts1.cpu(), verts2.cpu()).item()

def point_mesh_distance_score(verts1, faces1, verts2, faces2):
    mesh1 = Meshes(verts=[verts1], faces=[faces1])
    mesh2 = Meshes(verts=[verts2], faces=[faces2])
    
    if mesh1.isempty() or mesh2.isempty():
        print("Warning: Empty mesh detected")
        return float('inf')
    
    try:
        points1 = sample_points_from_meshes(mesh1, num_samples=5000)
        faces_idx = mesh2.faces_packed()  # Get faces of the second mesh
        verts_packed = mesh2.verts_packed()  # Get vertices of the second mesh

        point_to_face_distances = []
        for face in faces_idx:
            face_vertices = verts_packed[face]
            point_to_face_distances.append(torch.cdist(points1, face_vertices.unsqueeze(0)).min().item())
        
        return np.mean(point_to_face_distances)
    except Exception as e:
        print(f"Error in point_mesh_distance_score: {str(e)}")
        return float('inf')

def hausdorff_distance(verts1, verts2):
    from scipy.spatial.distance import directed_hausdorff
    return max(directed_hausdorff(verts1.cpu().numpy(), verts2.cpu().numpy())[0],
               directed_hausdorff(verts2.cpu().numpy(), verts1.cpu().numpy())[0])

def aad_score(verts1, faces1, verts2, faces2, num_samples=40000):
    if verts1 is None or verts2 is None:
        return 0.0
    
    mesh1 = Meshes(verts=[verts1], faces=[faces1])
    mesh2 = Meshes(verts=[verts2], faces=[faces2])
    
    samples1 = sample_points_from_meshes(mesh1, num_samples=num_samples)
    samples2 = sample_points_from_meshes(mesh2, num_samples=num_samples)
    
    normals1 = mesh1.verts_normals_packed()[torch.randint(len(mesh1.verts_packed()), (num_samples,))]
    normals2 = mesh2.verts_normals_packed()[torch.randint(len(mesh2.verts_packed()), (num_samples,))]
    
    aad1 = calculate_aad(samples1[0], normals1)
    aad2 = calculate_aad(samples2[0], normals2)
    
    hist1 = make_2d_histogram(aad1)
    hist2 = make_2d_histogram(aad2)
    
    return compare_2d_histograms(hist1, hist2)

def calculate_aad(points, normals):
    num_samples = len(points)
    indices = torch.randint(num_samples, (num_samples, 2))
    
    p1, p2 = points[indices[:, 0]], points[indices[:, 1]]
    n1, n2 = normals[indices[:, 0]], normals[indices[:, 1]]
    
    distances = torch.norm(p1 - p2, dim=1)
    angles = torch.abs(torch.sum(n1 * n2, dim=1))
    
    return torch.stack([distances, angles], dim=1)

def make_2d_histogram(aad, num_bins=(64, 8)):
    hist, _ = np.histogramdd(aad.cpu().numpy(), bins=num_bins, range=[[0, 1], [0, 1]])
    return hist

def compare_2d_histograms(hist1, hist2):
    hist1_flat = hist1.flatten()
    hist2_flat = hist2.flatten()
    correlation = np.corrcoef(hist1_flat, hist2_flat)[0, 1]
    similarity = (correlation + 1) / 2 * 100
    return similarity

def calculate_scores(answer_verts, answer_faces, student_verts, student_faces, device):
    cd = chamfer_distance_score(answer_verts, answer_faces, student_verts, student_faces, device)
    emd = earth_movers_distance(answer_verts, student_verts)
    pmd = point_mesh_distance_score(answer_verts, answer_faces, student_verts, student_faces)
    hd = hausdorff_distance(answer_verts, student_verts)
    aad = aad_score(answer_verts, answer_faces, student_verts, student_faces)
    
    return {
        "ChamferDistance": cd,
        "EarthMoversDistance": emd,
        "PointMeshDistance": pmd,
        "HausdorffDistance": hd,
        "AADSimilarity": aad
    }

def save_json(results, result_path):
    os.makedirs(result_path, exist_ok=True)
    with open(os.path.join(result_path, "results.json"), "w") as json_file:
        json.dump(results, json_file, indent=4)

if __name__ == "__main__":
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    results = {}

    
    # Load answer STL
    answer_verts, answer_faces = load_stl(ANS_STL_PATH, device)
    scores = calculate_scores(answer_verts, answer_faces, answer_verts, answer_faces, device)
    results['answer'] = scores
    
    
    # Process each student STL file
    for file in os.listdir(STL_PATH):
        print(f"Processing file {file}")
        if file.endswith(".stl"):
            file_name = file.split(".")[0]
            file_full_path = os.path.join(STL_PATH, file)
            
            try:
                student_verts, student_faces = load_stl(file_full_path, device)
                scores = calculate_scores(answer_verts, answer_faces, student_verts, student_faces, device)
                results[file_name] = scores
            except Exception as e:
                print(f"Error processing file {file_name}: {str(e)}")
                results[file_name] = {
                    "ChamferDistance": float('inf'),
                    "EarthMoversDistance": float('inf'),
                    "PointMeshDistance": float('inf'),
                    "HausdorffDistance": float('inf')
                }
    
    save_json(results, RESULT_PATH)
    print("Grading completed. Results saved in results.json")