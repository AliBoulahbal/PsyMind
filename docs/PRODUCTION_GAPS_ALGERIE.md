# Écarts fonctionnels et critères de lancement — Algérie

Cette liste empêche de confondre la base technique PsyMind V3 avec un produit clinique complet. Les modules ci-dessous doivent être vérifiés/complétés avant de les commercialiser comme disponibles.

## Socle présent à valider
- Patients, consultations, diagnostics, médicaments, allergies, prescriptions.
- Documents cliniques, extraction de texte, découpage, recherche RAG et gateway IA.
- Authentification JWT, permissions, tenant, migrations et journaux d'audit.
- Tableau de bord initial et interface web de démarrage.

## Écarts fonctionnels à fermer
- Rendez-vous, calendrier multi-praticiens, salles et gestion des absences.
- Admission, transfert, sortie, lits, services et parcours hospitalier.
- Facturation, actes, devis, paiements, remboursements, conventions et exports comptables adaptés aux règles locales.
- Laboratoire, demandes d'analyses, résultats, imagerie et intégrations externes.
- Pharmacie, stock, lots, péremption et règles de prescription validées localement.
- Portail patient, consentements, demandes d'accès/correction/suppression et gestion de rétention.
- Administration multi-utilisateur complète, MFA/SSO, invitations, réinitialisation de mot de passe et révocation des sessions.
- Workflow d'approbation réellement appliqué aux actions sensibles, avec contrôle des rôles et journalisation.
- Localisation française/arabe vérifiée dans toutes les pages, formulaires, exports PDF et emails ; support RTL.
- Import/export, migration des données, archivage et procédure de sortie client.
- Supervision complète, alertes, gestion d'incidents, reprise après sinistre et mises à jour signées.

## Validation clinique et réglementaire
- Définir les usages autorisés de l'IA et les usages interdits avec des cliniciens responsables.
- Créer un jeu de validation clinique représentatif et approuvé ; mesurer exactitude, omissions, citations, biais et taux de refus.
- Revue des textes algériens applicables, obligations ANPDP, secret médical, hébergement, sous-traitants et transferts éventuels.
- Revue des responsabilités contractuelles, consentements, durées de conservation et gestion des violations de données.

## Critère de lancement
Aucun module non testé ne doit être présenté comme fonctionnel. Lancer d'abord un pilote fermé avec données synthétiques, puis un pilote clinique encadré seulement après validation juridique, clinique, sécurité et restauration. Le lancement général doit dépendre des résultats documentés de ce pilote.
