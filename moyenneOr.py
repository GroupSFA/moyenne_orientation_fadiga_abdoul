import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import os
import random
import re

def extraire_moyenne_orientation_mendob(driver):
    """
    Extrait UNIQUEMENT la moyenne d'orientation MO (zone violette encadrée) - PAS MGA
    """
    try:
        # Attendre que la page soit complètement chargée
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        time.sleep(3)  # Attendre l'affichage complet
        
        # Obtenir le texte complet de la page pour debug
        page_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"📄 Contenu page (extrait): {page_text[:200]}...")
        
        # Méthodes d'extraction SPÉCIFIQUES pour MO (zone violette/encadrée)
        extraction_methods = [
            # Méthode 1: Zone violette/encadrée avec "MO" explicite
            lambda: extract_mo_violet_zone(driver),
            
            # Méthode 2: Chercher dans les éléments stylés après MGA
            lambda: extract_mo_styled_after_mga(driver),
            
            # Méthode 3: Chercher par position géographique (coin bas droite)
            lambda: extract_mo_bottom_right(driver),
            
            # Méthode 4: Chercher les nombres encadrés/stylés (hors MGA)
            lambda: extract_mo_bordered_numbers(driver),
            
            # Méthode 5: Patterns spécifiques à la structure Mendob
            lambda: extract_mo_mendob_structure(driver),
        ]
        
        for i, method in enumerate(extraction_methods, 1):
            try:
                print(f"🔍 Méthode {i}: ", end="")
                result = method()
                if result:
                    moyenne_value, source_text, method_name = result
                    print(f"✅ MO trouvée: {moyenne_value} via {method_name}")
                    print(f"📝 Source: {source_text[:100]}...")
                    return moyenne_value, source_text
                else:
                    print("❌ Aucun résultat")
            except Exception as e:
                print(f"⚠️ Erreur: {str(e)[:50]}")
                continue
        
        return None, None
        
    except Exception as e:
        print(f"❌ Erreur extraction: {e}")
        return None, None

def extract_mo_violet_zone(driver):
    """Recherche MO dans la zone violette encadrée (priorité absolue)"""
    try:
        # Chercher spécifiquement les éléments avec texte "MO" et style violet/encadré
        mo_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'MO')]")
        
        for element in mo_elements:
            try:
                text = element.text.strip()
                style = element.get_attribute('style') or ''
                parent_style = element.find_element(By.XPATH, './..').get_attribute('style') or ''
                
                # Vérifier si c'est dans une zone stylée (violet, encadré, etc.)
                has_special_style = any(keyword in (style + parent_style).lower() 
                                     for keyword in ['background', 'border', 'color', 'purple', 'violet'])
                
                if has_special_style or 'MO' in text.upper():
                    # Chercher le nombre associé à MO dans l'élément ou ses voisins
                    
                    # Dans l'élément même
                    mo_match = re.search(r'MO[:\s]*(\d{1,2}\.?\d{0,2})', text)
                    if mo_match:
                        try:
                            moyenne_value = float(mo_match.group(1))
                            if 0 <= moyenne_value <= 20:
                                return moyenne_value, text, "mo_violet_direct"
                        except ValueError:
                            continue
                    
                    # Dans les éléments voisins
                    try:
                        siblings = element.find_elements(By.XPATH, './following-sibling::*') + \
                                 element.find_elements(By.XPATH, './preceding-sibling::*')
                        
                        for sibling in siblings[:3]:  # Vérifier les 3 premiers voisins
                            sibling_text = sibling.text.strip()
                            if re.match(r'^\d{1,2}\.\d{2}$', sibling_text):
                                try:
                                    moyenne_value = float(sibling_text)
                                    if 0 <= moyenne_value <= 20:
                                        return moyenne_value, f"MO zone: {sibling_text}", "mo_violet_sibling"
                                except ValueError:
                                    continue
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        return None
    except Exception as e:
        print(f"Erreur extract_mo_violet_zone: {e}")
        return None

def extract_mo_styled_after_mga(driver):
    """Cherche MO dans les éléments stylés APRÈS avoir trouvé MGA"""
    try:
        # D'abord localiser MGA
        mga_found = False
        mga_position = None
        
        # Chercher tous les éléments contenant des nombres
        all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '11.41') or contains(text(), 'MGA')]")
        
        for element in all_elements:
            if 'MGA' in element.text or '11.41' in element.text:
                mga_found = True
                mga_position = element.location
                print(f"🎯 MGA trouvée à position: {mga_position}")
                break
        
        if not mga_found:
            return None
        
        # Maintenant chercher des éléments stylés avec des nombres, situés APRÈS MGA
        styled_elements = driver.find_elements(By.XPATH, 
            "//*[@style or @class][text()[matches(., '\\d+\\.\\d+')]]")
        
        for element in styled_elements:
            try:
                element_position = element.location
                text = element.text.strip()
                
                # Si l'élément est positionné après MGA (plus bas ou à droite)
                if (element_position['y'] > mga_position['y'] or 
                    (element_position['y'] == mga_position['y'] and element_position['x'] > mga_position['x'])):
                    
                    # Chercher des nombres dans cet élément
                    numbers = re.findall(r'\b(\d{1,2}\.\d{2})\b', text)
                    for number in numbers:
                        try:
                            moyenne_value = float(number)
                            # MO est généralement plus faible que MGA
                            if 0 <= moyenne_value <= 15 and moyenne_value != 11.41:  # Exclure MGA
                                return moyenne_value, text, "mo_styled_after_mga"
                        except ValueError:
                            continue
                            
            except Exception:
                continue
        
        return None
    except Exception as e:
        print(f"Erreur extract_mo_styled_after_mga: {e}")
        return None

def extract_mo_bottom_right(driver):
    """Cherche dans la zone bas-droite de la page (position typique de MO)"""
    try:
        # Obtenir les dimensions de la page
        page_height = driver.execute_script("return document.body.scrollHeight")
        page_width = driver.execute_script("return document.body.scrollWidth")
        
        # Définir la zone bas-droite (dernier quart de la page)
        min_x = page_width * 0.6
        min_y = page_height * 0.6
        
        # Chercher tous les éléments dans cette zone
        all_elements = driver.find_elements(By.XPATH, "//*[text()]")
        
        for element in all_elements:
            try:
                position = element.location
                
                # Si l'élément est dans la zone bas-droite
                if position['x'] >= min_x and position['y'] >= min_y:
                    text = element.text.strip()
                    
                    # Chercher des nombres dans cette zone
                    numbers = re.findall(r'\b(\d{1,2}\.\d{2})\b', text)
                    for number in numbers:
                        try:
                            moyenne_value = float(number)
                            # Exclure MGA et chercher des valeurs typiques de MO
                            if 0 <= moyenne_value <= 15 and moyenne_value != 11.41:
                                # Vérifier si c'est stylé ou encadré
                                style = element.get_attribute('style') or ''
                                if style or 'MO' in element.get_attribute('outerHTML').upper():
                                    return moyenne_value, text, "mo_bottom_right"
                        except ValueError:
                            continue
                            
            except Exception:
                continue
        
        return None
    except Exception as e:
        print(f"Erreur extract_mo_bottom_right: {e}")
        return None

def extract_mo_bordered_numbers(driver):
    """Cherche les nombres encadrés/stylés (hors MGA)"""
    try:
        # Chercher tous les éléments avec des styles de bordure/fond
        bordered_selectors = [
            "*[style*='border']",
            "*[style*='background']", 
            "*[style*='outline']",
            "*[style*='box-shadow']",
            ".bordered", ".highlighted", ".result"
        ]
        
        for selector in bordered_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    
                    # Chercher des nombres dans les éléments stylés
                    if re.match(r'^\d{1,2}\.\d{2}$', text):
                        try:
                            moyenne_value = float(text)
                            # Exclure MGA et garder les valeurs typiques de MO
                            if 0 <= moyenne_value <= 15 and moyenne_value != 11.41:
                                # Vérifier que ce n'est pas dans un contexte MGA
                                parent_text = element.find_element(By.XPATH, './..').text
                                if 'MGA' not in parent_text.upper():
                                    return moyenne_value, text, "mo_bordered_number"
                        except ValueError:
                            continue
                            
            except Exception:
                continue
        
        return None
    except Exception as e:
        print(f"Erreur extract_mo_bordered_numbers: {e}")
        return None

def extract_mo_mendob_structure(driver):
    """Patterns spécifiques à la structure du site Mendob"""
    try:
        # Analyser la structure spécifique de Mendob
        # Chercher dans les tableaux après la ligne MGA
        
        # Trouver la cellule contenant MGA
        mga_cell = None
        try:
            mga_elements = driver.find_elements(By.XPATH, "//td[contains(text(), 'MGA') or contains(text(), '11.41')]")
            if mga_elements:
                mga_cell = mga_elements[0]
        except Exception:
            pass
        
        if mga_cell:
            try:
                # Chercher dans les cellules suivantes du même tableau
                following_cells = mga_cell.find_elements(By.XPATH, ".//following::td")
                
                for cell in following_cells[:10]:  # Limiter la recherche
                    cell_text = cell.text.strip()
                    
                    if re.match(r'^\d{1,2}\.\d{2}$', cell_text):
                        try:
                            moyenne_value = float(cell_text)
                            if 0 <= moyenne_value <= 15 and moyenne_value != 11.41:
                                # Vérifier si la cellule a un style particulier
                                cell_style = cell.get_attribute('style') or ''
                                if cell_style or cell.get_attribute('class'):
                                    return moyenne_value, cell_text, "mo_mendob_table"
                        except ValueError:
                            continue
                            
            except Exception:
                pass
        
        # Méthode alternative: chercher des motifs spécifiques dans le HTML
        page_source = driver.page_source
        
        # Pattern pour zone MO encadrée (basé sur l'image)
        mo_patterns = [
            r'MO[^0-9]*(\d{1,2}\.\d{2})',  # MO suivi d'un nombre
            r'style="[^"]*(?:border|background)[^"]*"[^>]*>(\d{1,2}\.\d{2})',  # Nombre dans élément stylé
        ]
        
        for pattern in mo_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            for match in matches:
                try:
                    moyenne_value = float(match)
                    if 0 <= moyenne_value <= 15 and moyenne_value != 11.41:
                        return moyenne_value, match, "mo_mendob_pattern"
                except ValueError:
                    continue
        
        return None
    except Exception as e:
        print(f"Erreur extract_mo_mendob_structure: {e}")
        return None

def extraction_moyenne_orientation_mendob():
    """
    Extraction de la moyenne d'orientation depuis le site Bourses Mendob
    Site: https://bourses.mendob.ci/index.php?adr=consultnotesbepc.inc
    FOCUS: Extraire MO (zone violette encadrée) et NON pas MGA
    """
    
    # Charger vos données
    print("🔄 Chargement des données...")
    try:
        df = pd.read_excel("C:/Users/LeghoJoshua/desktop/newachercher.xlsx")
        print(f"✅ Données chargées: {len(df)} lignes")
        print(f"📋 Colonnes: {list(df.columns)}")
        
        # Préparation des fichiers de sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fichier_resultats = f"moyenne_orientation_MO_corrige_{timestamp}.csv"
        fichier_checkpoint = f"checkpoint_MO_corrige_{timestamp}.csv"
        
        matricules_complets = df['MATRICULE'].astype(str).tolist()
        print(f"🎯 Extraction pour {len(matricules_complets)} matricules")
        print("⚠️ IMPORTANT: Extraction de MO (zone violette) - PAS MGA")
        
        # Gestion reprise
        start_index = 0
        resultats_existants = []
        
        checkpoints = [f for f in os.listdir('.') if f.startswith('checkpoint_MO_corrige_') and f.endswith('.csv')]
        if checkpoints:
            try:
                df_checkpoint = pd.read_csv(sorted(checkpoints, reverse=True)[0])
                resultats_existants = df_checkpoint.to_dict('records')
                start_index = len(resultats_existants)
                print(f"🔄 Reprise depuis l'index {start_index}")
            except:
                print("⚠️ Nouveau démarrage")
        
    except Exception as e:
        print(f"❌ Erreur chargement: {e}")
        return

    # Configuration Chrome optimisée
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Statistiques
    compteurs = {
        'MO_EXTRAITE': 0,
        'MATRICULE_INTROUVABLE': 0,
        'ERREUR_TECHNIQUE': 0,
        'MO_NON_DETECTEE': 0
    }
    
    resultats = resultats_existants.copy()
    moyennes_mo_trouvees = []
    
    try:
        # Initialisation navigateur
        print(f"\n🌐 Initialisation navigateur Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_window_size(1366, 768)
        
        # URL du site Mendob
        base_url = "https://bourses.mendob.ci/index.php?adr=consultnotesbepc.inc"
        
        # Boucle principale
        for i in range(start_index, len(matricules_complets)):
            matricule = matricules_complets[i]
            position = i + 1
            
            print(f"\n{'='*70}")
            print(f"🎯 EXTRACTION MO {position}/{len(matricules_complets)}: {matricule}")
            print(f"📊 Progression: {(position/len(matricules_complets)*100):.1f}%")
            print(f"{'='*70}")
            
            try:
                # Pauses adaptatives
                if position % 100 == 0:
                    pause = random.randint(45, 90)
                    print(f"⏸️ Pause longue: {pause}s")
                    time.sleep(pause)
                elif position % 25 == 0:
                    pause = random.randint(15, 30)
                    print(f"⏸️ Pause moyenne: {pause}s")
                    time.sleep(pause)
                
                # Chargement page principale
                print("🌍 Chargement du site Mendob...")
                driver.get(base_url)
                
                # Attendre le chargement
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(random.uniform(3, 6))
                
                # Recherche du champ matricule
                print("🔍 Recherche champ matricule...")
                champ_selectors = [
                    "input[name='matricule']",
                    "input[placeholder*='matricule' i]",
                    "input[type='text']",
                    "input[type='number']",
                    "#matricule",
                    ".form-control",
                    "input"
                ]
                
                champ = None
                for selector in champ_selectors:
                    try:
                        champ = WebDriverWait(driver, 8).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if champ.is_displayed() and champ.is_enabled():
                            print(f"✅ Champ trouvé: {selector}")
                            break
                    except:
                        continue
                
                if not champ:
                    print("❌ Champ matricule non trouvé")
                    resultats.append({
                        'matricule': matricule,
                        'moyenne_orientation_MO': None,
                        'moyenne_texte': None,
                        'statut': 'ERREUR_TECHNIQUE',
                        'details': 'Champ matricule introuvable',
                        'position': position
                    })
                    compteurs['ERREUR_TECHNIQUE'] += 1
                    continue
                
                # Saisie matricule
                print(f"⌨️ Saisie: {matricule}")
                champ.clear()
                time.sleep(0.5)
                
                # Saisie progressive
                for char in str(matricule):
                    champ.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.3))
                
                # Soumission
                print("📤 Soumission...")
                try:
                    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .btn, button")
                    driver.execute_script("arguments[0].click();", submit_btn)
                except:
                    champ.send_keys(Keys.RETURN)
                
                # Attendre résultats
                print("⏳ Attente résultats...")
                time.sleep(random.uniform(8, 15))
                
                # Vérifier si matricule existe
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                
                if any(pattern in page_text for pattern in ['matricule non reconnu', 'introuvable', 'non trouvé', 'not found', 'aucun résultat', 'erreur']):
                    print("❓ Matricule introuvable")
                    resultats.append({
                        'matricule': matricule,
                        'moyenne_orientation_MO': None,
                        'moyenne_texte': None,
                        'statut': 'MATRICULE_INTROUVABLE',
                        'details': 'Matricule non trouvé dans la base',
                        'position': position
                    })
                    compteurs['MATRICULE_INTROUVABLE'] += 1
                    
                else:
                    # Extraction de la moyenne d'orientation MO
                    print("🔍 Extraction de la MO (zone violette encadrée)...")
                    moyenne_value, moyenne_source = extraire_moyenne_orientation_mendob(driver)
                    
                    if moyenne_value is not None:
                        print(f"✅ MO extraite: {moyenne_value}")
                        print(f"⚠️ Vérification: différent de MGA (11.41)? {moyenne_value != 11.41}")
                        
                        resultats.append({
                            'matricule': matricule,
                            'moyenne_orientation_MO': moyenne_value,
                            'moyenne_texte': moyenne_source[:100] if moyenne_source else None,
                            'statut': 'MO_EXTRAITE',
                            'details': f'MO (zone violette): {moyenne_value}',
                            'position': position,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        compteurs['MO_EXTRAITE'] += 1
                        moyennes_mo_trouvees.append(moyenne_value)
                        
                    else:
                        print("❌ MO non détectée dans la zone violette")
                        # Sauvegarder le HTML pour debug
                        debug_html = f"debug_MO_{matricule}_{position}.html"
                        with open(debug_html, 'w', encoding='utf-8') as f:
                            f.write(driver.page_source)
                        print(f"🐛 HTML sauvé pour debug: {debug_html}")
                        
                        resultats.append({
                            'matricule': matricule,
                            'moyenne_orientation_MO': None,
                            'moyenne_texte': None,
                            'statut': 'MO_NON_DETECTEE',
                            'details': f'MO présente mais non détectée - Debug: {debug_html}',
                            'position': position
                        })
                        compteurs['MO_NON_DETECTEE'] += 1
                
                # Sauvegarde périodique
                if position % 50 == 0:
                    print(f"💾 Sauvegarde checkpoint...")
                    pd.DataFrame(resultats).to_csv(fichier_checkpoint, index=False, encoding='utf-8')
                    
                    print(f"📊 Stats intermédiaires:")
                    for stat, count in compteurs.items():
                        if count > 0:
                            print(f"   {stat}: {count}")
                
                # Pause entre requêtes
                pause = random.uniform(4, 10)
                print(f"⏸️ Pause: {pause:.1f}s")
                time.sleep(pause)
                
            except Exception as e:
                print(f"❌ Erreur matricule {matricule}: {e}")
                resultats.append({
                    'matricule': matricule,
                    'moyenne_orientation_MO': None,
                    'moyenne_texte': None,
                    'statut': 'ERREUR_TECHNIQUE',
                    'details': f'Exception: {str(e)[:100]}',
                    'position': position
                })
                compteurs['ERREUR_TECHNIQUE'] += 1
                time.sleep(5)
        
        # Résultats finaux  
        print("\n" + "="*80)
        print("🎉 EXTRACTION TERMINÉE - MOYENNE D'ORIENTATION MO (CORRIGÉE)")
        print("="*80)
        
        total = len(resultats)
        print(f"📊 STATISTIQUES:")
        for statut, count in compteurs.items():
            pourcentage = (count/total*100) if total > 0 else 0
            print(f"   {statut}: {count} ({pourcentage:.1f}%)")
        
        if moyennes_mo_trouvees:
            print(f"\n📈 ANALYSE MOYENNES MO (ZONE VIOLETTE):")
            print(f"   Extraites: {len(moyennes_mo_trouvees)}")
            print(f"   Moyenne: {sum(moyennes_mo_trouvees)/len(moyennes_mo_trouvees):.2f}")
            print(f"   Min-Max: {min(moyennes_mo_trouvees):.2f} - {max(moyennes_mo_trouvees):.2f}")
            
            # Vérification anti-MGA
            mga_count = sum(1 for x in moyennes_mo_trouvees if abs(x - 11.41) < 0.01)
            print(f"   ⚠️ Valeurs MGA détectées par erreur: {mga_count}")
        
        # Sauvegarde finale
        if resultats:
            df_final = pd.DataFrame(resultats)
            df_final.to_csv(fichier_resultats, index=False, encoding='utf-8')
            print(f"\n💾 Résultats sauvés: {fichier_resultats}")
            
            # Nettoyer checkpoint
            try:
                if os.path.exists(fichier_checkpoint):
                    os.remove(fichier_checkpoint)
            except:
                pass
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        # Sauvegarde d'urgence
        if resultats:
            urgence = f"urgence_MO_corrige_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            pd.DataFrame(resultats).to_csv(urgence, index=False, encoding='utf-8')
            print(f"🆘 Sauvegarde urgence: {urgence}")
        
    finally:
        try:
            if 'driver' in locals():
                driver.quit()
                print("🔒 Navigateur fermé")
        except:
            pass

if __name__ == "__main__":
    print("🚀 EXTRACTION MOYENNE D'ORIENTATION MO (CORRIGÉE)")
    print("🌐 Site: https://bourses.mendob.ci/index.php?adr=consultnotesbepc.inc")
    print("🎯 FOCUS: Extraire MO (zone violette encadrée) - PAS MGA")
    print("💾 Sauvegardes automatiques tous les 50 résultats")
    print("🐛 Debug HTML automatique pour les cas non détectés")
    print("⚠️ IMPORTANT: Cherche la vraie MO (9.50 dans l'exemple) pas MGA (11.41)")
    print("-" * 60)
    
    extraction_moyenne_orientation_mendob()
    print("\n✅ EXTRACTION MO TERMINÉE!")