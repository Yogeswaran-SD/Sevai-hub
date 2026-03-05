import React from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function ServiceCard({ service }) {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <div
      className="service-card"
      style={{ "--card-color": service.color }}
      onClick={() => navigate(`/search?category=${service.category}`)}
    >
      <div className="service-icon">{service.icon}</div>
      <div>
        <div className="service-name">{t(`home.services.${service.category}.name`, service.name)}</div>
        <div className="service-desc">{t(`home.services.${service.category}.description`, service.description)}</div>
      </div>
      <div className="service-arrow">
        {t('home.findNearby', 'Find nearby')} →
      </div>
    </div>
  );
}
