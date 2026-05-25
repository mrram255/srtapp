"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth-store";
import { studyMaterialsApi, type StudyMaterial } from "@/lib/api/study-materials";

export default function StudyMaterialsPage() {
  const user = useAuthStore((s) => s.user);
  const [materials, setMaterials] = useState<StudyMaterial[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadMsg, setUploadMsg] = useState("");

  const isTeacher = ["TEACHER", "HOD", "ADMIN", "SUPER_ADMIN"].includes(user?.role ?? "");

  const handleUpload = async (file: File) => {
    if (!uploadTitle.trim()) {
      setUploadMsg("Title required before upload.");
      return;
    }
    try {
      setUploading(true);
      const up = await studyMaterialsApi.upload(file);
      const fileUrl = up.data?.file_url ?? up.data?.url ?? "";
      await studyMaterialsApi.create({
        title: uploadTitle,
        material_type: "PDF",
        file_url: fileUrl,
        is_published: true,
      });
      setUploadMsg("Material uploaded.");
      setUploadTitle("");
      const res = await studyMaterialsApi.list();
      setMaterials(res.data?.items ?? res.data ?? []);
    } catch (e: unknown) {
      setUploadMsg(e instanceof Error ? e.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    if (!user?.id) return;
    const fetchData = async () => {
      try {
        setLoading(true);
        const params: Record<string, string> = {};
        if (search) params.search = search;
        if (filterType) params.type = filterType;
        const res = await studyMaterialsApi.list(params);
        setMaterials(res.data?.items ?? res.data ?? []);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load study materials.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user?.id, search, filterType]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600" />
          <p className="text-sm text-gray-400">Loading study materials...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="m-6 p-5 bg-red-50 border border-red-200 rounded-xl text-red-700 flex items-center gap-3">
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Study Materials</h1>
          <p className="text-sm text-gray-500 mt-0.5">Access your course resources</p>
        </div>
        <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium">
          {materials.length} Materials
        </span>
      </div>

      {isTeacher ? (
        <div className="rounded-xl border border-gray-200 bg-white p-4 space-y-3">
          <p className="text-sm font-medium text-gray-800">Upload study material</p>
          <input value={uploadTitle} onChange={(e) => setUploadTitle(e.target.value)} placeholder="Title" className="w-full rounded-lg border px-3 py-2 text-sm" />
          <input type="file" accept=".pdf,.doc,.docx,.ppt,.pptx" onChange={(e) => { const f = e.target.files?.[0]; if (f) void handleUpload(f); }} className="text-sm" />
          {uploading ? <p className="text-sm text-gray-500">Uploading...</p> : null}
          {uploadMsg ? <p className="text-sm text-green-700">{uploadMsg}</p> : null}
        </div>
      ) : null}

      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Search materials..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 min-w-[200px] px-4 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-4 py-2 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="">All Types</option>
          <option value="PDF">PDF</option>
          <option value="VIDEO">VIDEO</option>
          <option value="IMAGE">IMAGE</option>
          <option value="DOCUMENT">DOCUMENT</option>
          <option value="LINK">LINK</option>
          <option value="OTHER">OTHER</option>
        </select>
      </div>

      {materials.length === 0 ? (
        <div className="text-center py-16 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
          <p className="text-gray-500 font-medium">No study materials found</p>
          <p className="text-gray-400 text-sm mt-1">Try changing your search or filter</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {materials.map((m) => (
            <MaterialCard key={m.id} material={m} />
          ))}
        </div>
      )}
    </div>
  );
}

function MaterialCard({ material }: { material: StudyMaterial }) {
  const typeColors: Record<string, string> = {
    PDF: "bg-red-50 border-red-100 text-red-700",
    VIDEO: "bg-purple-50 border-purple-100 text-purple-700",
    IMAGE: "bg-pink-50 border-pink-100 text-pink-700",
    DOCUMENT: "bg-blue-50 border-blue-100 text-blue-700",
    LINK: "bg-green-50 border-green-100 text-green-700",
    OTHER: "bg-gray-50 border-gray-100 text-gray-700",
  };

  const formatSize = (bytes: number) => {
    if (!bytes) return "";
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const url = material.file_url || material.external_link;
  const colorClass = typeColors[material.material_type] ?? typeColors["OTHER"];

  return (
    <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col gap-3">
      <div className="flex items-start gap-2 flex-wrap">
        <span className={"text-xs font-semibold px-2 py-0.5 rounded-full border " + colorClass}>
          {material.material_type}
        </span>
        {!material.is_published && (
          <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">
            Draft
          </span>
        )}
      </div>

      <h3 className="font-semibold text-gray-900">{material.title}</h3>

      {material.description && (
        <p className="text-sm text-gray-500 line-clamp-2">{material.description}</p>
      )}

      <div className="flex flex-wrap gap-3 text-xs text-gray-500">
        <span>{material.subject_name}</span>
        <span>{material.teacher_name}</span>
        <span>Sem {material.semester}</span>
        {material.file_size > 0 && <span>{formatSize(material.file_size)}</span>}
        <span>{material.download_count} downloads</span>
      </div>

      {material.tags_list.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {material.tags_list.map((tag) => (
            <span key={tag} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
              #{tag}
            </span>
          ))}
        </div>
      )}

      {url && (
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-auto inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          {material.material_type === "LINK" ? "Open Link" : "Download"}
        </a>
      )}
    </div>
  );
}
