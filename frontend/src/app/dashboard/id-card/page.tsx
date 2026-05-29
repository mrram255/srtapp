"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth-store";
import api from "@/lib/api/client";

interface IDCardData {
  user_id: string;
  name: string;
  email: string;
  phone: string;
  role: string;
  role_label: string;
  id_number: string;
  department: string;
  college_name: string;
  profile_photo: string;
  qr_code: string;
  valid_till: string;
  roll_number?: string;
  semester?: number;
  section?: string;
  blood_group?: string;
  designation?: string;
}

export default function IDCardPage() {
  const user = useAuthStore((s) => s.user);
  const [card, setCard] = useState<IDCardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (!user?.id) return;
    const fetchCard = async () => {
      try {
        setLoading(true);
        const res = await api.get("/students/id-card/me/").then((r) => r.data);
        setCard(res.data);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load ID card.");
      } finally {
        setLoading(false);
      }
    };
    fetchCard();
  }, [user?.id]);

  const handleDownload = async () => {
    try {
      setDownloading(true);
      const blob = await api.get("/students/id-card/me/", {
        params: { format: "pdf" },
        responseType: "blob",
      }).then((r) => r.data);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `id_card_${card?.id_number}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("Download failed.");
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600" />
          <p className="text-sm text-gray-400">Loading ID card...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="m-6 p-5 bg-red-50 border border-red-200 rounded-xl text-red-700">
        ⚠️ {error}
      </div>
    );
  }

  if (!card) return null;

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Digital ID Card</h1>
          <p className="text-sm text-gray-500 mt-0.5">Your official college identity card</p>
        </div>
        <button
          onClick={handleDownload}
          disabled={downloading}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {downloading ? "⏳ Downloading..." : "⬇️ Download PDF"}
        </button>
      </div>

      {/* ID Card */}
      <div className="relative rounded-2xl overflow-hidden shadow-2xl" style={{ background: "linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)" }}>
        {/* Header */}
        <div className="px-6 pt-5 pb-3 text-center">
          <div className="flex items-center justify-center gap-2 mb-1">
            <span className="text-white text-2xl">🎓</span>
            <h2 className="text-white font-bold text-lg uppercase tracking-wide">
              {card.college_name}
            </h2>
          </div>
          <p className="text-blue-200 text-xs font-medium tracking-widest uppercase">
            {card.role_label} Identity Card
          </p>
        </div>

        {/* Card Body */}
        <div className="mx-4 mb-4 bg-white rounded-xl p-5">
          <div className="flex gap-5">
            {/* Photo */}
            <div className="flex-shrink-0">
              <div className="w-24 h-28 bg-gray-100 rounded-xl overflow-hidden border-2 border-blue-100 flex items-center justify-center">
                {card.profile_photo ? (
                  <Image src={card.profile_photo} alt="Photo" width={200} height={200} className="w-full h-full object-cover" />
                ) : (
                  <span className="text-5xl">👤</span>
                )}
              </div>
            </div>

            {/* Info */}
            <div className="flex-1 space-y-2">
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wide">Name</p>
                <p className="font-bold text-gray-900 text-lg leading-tight">{card.name}</p>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <InfoItem label="ID Number" value={card.id_number} />
                <InfoItem label="Role" value={card.role_label} />
                <InfoItem label="Department" value={card.department || "N/A"} />
                <InfoItem label="Email" value={card.email} />
                {card.semester && <InfoItem label="Semester" value={`Sem ${card.semester} | Sec ${card.section}`} />}
                {card.blood_group && <InfoItem label="Blood Group" value={card.blood_group} highlight />}
                {card.designation && <InfoItem label="Designation" value={card.designation} />}
              </div>
            </div>
          </div>

          <div className="border-t border-gray-100 my-4" />

          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Valid Till</p>
              <p className="font-bold text-blue-700 text-lg">{card.valid_till}</p>
              <p className="text-xs text-gray-400 mt-2">Scan QR to verify</p>
            </div>
            {card.qr_code && (
              <img
                src={`data:image/png;base64,${card.qr_code}`}
                alt="QR Code"
                className="w-24 h-24 rounded-lg border border-gray-100"
              />
            )}
          </div>
        </div>

        <div className="px-6 pb-4 text-center">
          <p className="text-blue-200 text-xs">
            If found, please return to the college • Non-transferable
          </p>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 flex gap-3">
        <span className="text-2xl">🔒</span>
        <div>
          <p className="font-semibold text-blue-800 text-sm">Secure Digital ID</p>
          <p className="text-blue-600 text-xs mt-0.5">
            QR code contains verified information. Scan to instantly verify authenticity.
          </p>
        </div>
      </div>
    </div>
  );
}

function InfoItem({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div>
      <p className="text-xs text-gray-400 uppercase tracking-wide">{label}</p>
      <p className={`text-sm font-semibold truncate ${highlight ? "text-red-600" : "text-gray-800"}`}>{value}</p>
    </div>
  );
}
