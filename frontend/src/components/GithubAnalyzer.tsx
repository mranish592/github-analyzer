import React, { useState } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { submitAnalysis } from '@/api/api';
import { getAnalysisResult } from '@/api/api';
import { getAnalysisStatus } from '@/api/api';

// Update interfaces to match backend models
interface ExperienceMetrics {
  lines_of_code: number;
  first_commit_timestamp: string;
  last_commit_timestamp: string;
  repos: string[];
}

interface QualityMetrics {
  bugs_per_commit: number | null;
  code_smells_per_commit: number | null;
  complexity_per_commit: number | null;
  vulnerabilities_per_commit: number | null;
  code_coverage: number | null;
  duplicated_lines_density: number | null;
  reliability_rating: string | null;
  security_rating: string | null;
  maintainability_rating: string | null;
}

interface OverallExperienceMetrics {
  skills: Record<string, ExperienceMetrics>;
}

interface OverallQualityMetrics {
  skills: Record<string, QualityMetrics>;
}

interface AnalysisStatus {
  total_commits: number;
  analyzed_commits: number;
  analysis_completed: boolean;
}

interface AnalyzeResponse {
  username: string;
  name: string;
  message: string;
  experience_metrics: OverallExperienceMetrics | null;
  quality_metrics: OverallQualityMetrics | null;
}

// interface SubmitAnalysisResponse {
//   username: string;
//   analysis_id: string;
//   name: string;
// }

interface StatusResponse {
  analysis_id: string;
  status: AnalysisStatus;
}

type ScanType = 'quick' | 'deep';

export default function GitHubAnalyzer() {
  const [username, setUsername] = useState<string>('');
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [_, setAnalysisId] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<AnalyzeResponse | null>(null);
  const [statusResponse, setStatusResponse] = useState<StatusResponse | null>(null);
  
  // Convert backend data to UI format for experience tab
  const experienceData = React.useMemo(() => {
    if (!analysisData?.experience_metrics) return [];
    
    return Object.entries(analysisData.experience_metrics.skills).map(([language, metrics]) => {
      // Calculate experience duration from first commit to now
      const firstCommit = new Date(metrics.first_commit_timestamp);
      const currentDate = new Date();
      const durationMs = currentDate.getTime() - firstCommit.getTime();
      const durationDays = Math.floor(durationMs / (1000 * 60 * 60 * 24));
      
      let usingSince = '';
      if (durationDays < 30) {
        usingSince = durationDays === 1 ? '1 Day' : `${durationDays} Days`;
      } else if (durationDays < 365) {
        const months = Math.floor(durationDays / 30);
        usingSince = months === 1 ? '1 Month' : `${months} Months`;
      } else {
        const years = Math.floor(durationDays / 365);
        usingSince = years === 1 ? '1 Year' : `${years} Years`;
      }
      
      return {
        language,
        linesOfCode: metrics.lines_of_code,
        repositories: metrics.repos.length,
        usingSince
      };
    });
  }, [analysisData]);

  // Convert backend data to UI format for code quality tab
  const codeQualityData = React.useMemo(() => {
    if (!analysisData?.quality_metrics) return [];
    
    return Object.entries(analysisData.quality_metrics.skills).map(([language, metrics]) => {
      return {
        language,
        reliabilityRating: metrics.reliability_rating || 'N/A',
        securityRating: metrics.security_rating || 'N/A',
        maintainabilityRating: metrics.maintainability_rating || 'N/A',
        duplicatedLinesDensity: metrics.duplicated_lines_density ? `${metrics.duplicated_lines_density}%` : 'N/A',
        vulnerabilityPerCommit: metrics.vulnerabilities_per_commit || 0,
        bugsPerCommit: metrics.bugs_per_commit || 0,
        codeSmellsPerCommit: metrics.code_smells_per_commit || 0,
        complexityPerCommit: metrics.complexity_per_commit || 0
      };
    });
  }, [analysisData]);

  // Poll for analysis status
  const pollStatus = async (id: string) => {
    try {
      const response = await getAnalysisStatus(id);
      setStatusResponse(response);
      const { status } = response;
      
      if (status.total_commits > 0) {
        const newProgress = Math.floor((status.analyzed_commits / status.total_commits) * 100);
        setProgress(newProgress);
      }
      
      if (status.analysis_completed) {
        const result = await getAnalysisResult(id);
        setAnalysisData(result);
        setIsScanning(false);
        setProgress(100);
        return;
      }
      
      // Continue polling if not complete
      setTimeout(() => pollStatus(id), 2000);
    } catch (error) {
      console.error('Error polling status:', error);
      setIsScanning(false);
    }
  };

  const startScan = async (type: ScanType): Promise<void> => {
    setIsScanning(true);
    setProgress(0);
    setAnalysisData(null);
    
    try {
      // Deep scan uses the full analysis, quick scan skips quality metrics
      const skipQualityMetrics = type === 'quick';
      
      const response = await submitAnalysis(username, skipQualityMetrics);
      setAnalysisId(response.analysis_id);
      
      // Start polling for status
      pollStatus(response.analysis_id);
    } catch (error) {
      console.error('Error starting scan:', error);
      setIsScanning(false);
    }
  };

  const getRatingColor = (rating: string): string => {
    switch(rating) {
      case 'A': return 'bg-emerald-100 text-emerald-800 hover:bg-emerald-200';
      case 'B': return 'bg-blue-100 text-blue-800 hover:bg-blue-200';
      case 'C': return 'bg-amber-100 text-amber-800 hover:bg-amber-200';
      case 'D': return 'bg-orange-100 text-orange-800 hover:bg-orange-200';
      default: return 'bg-red-100 text-red-800 hover:bg-red-200';
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">GitHub Analyzer</h1>
      
      <div className="flex gap-4 mb-6">
        <Input 
          placeholder="Enter GitHub username" 
          value={username}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)}
          className="flex-grow"
        />
        <Button 
          onClick={() => startScan('quick')}
          disabled={isScanning || !username}
          className="text-white bg-gradient-to-br from-teal-600 to-teal-700 shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:shadow-none"
        >
          Quick Scan
        </Button>
        <Button 
          onClick={() => startScan('deep')}
          disabled={isScanning || !username}
          className="text-white bg-gradient-to-br from-slate-600 to-slate-700 shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:shadow-none"
        >
          Deep Scan
        </Button>
      </div>
      
      {isScanning && (
        <div className="mb-6">
          <div className="flex justify-between mb-2">
            <p className="text-sm text-gray-500">Scanning in progress...</p>
            <p className="text-sm text-gray-500">
              {statusResponse?.status?.total_commits ? 
                `${statusResponse.status.analyzed_commits || 0}/${statusResponse.status.total_commits} commits` : 
                'Initializing...'
              }
            </p>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      )}
      
      <Tabs defaultValue="experience" className="mt-8">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="experience">Experience</TabsTrigger>
          <TabsTrigger value="codeQuality">Code Quality</TabsTrigger>
        </TabsList>
        
        <TabsContent value="experience">
          <Card className="shadow-sm">
            <CardHeader className="bg-gray-50">
              <CardTitle>Experience</CardTitle>
            </CardHeader>
            <CardContent>
              {experienceData.map((item, index) => (
                <div key={index} className="mb-6 pb-6 border-b last:border-0">
                  <h3 className="text-xl font-semibold mb-3">{item.language}</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Lines of code written</p>
                      <p className="font-medium">{item.linesOfCode.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Repositories</p>
                      <p className="font-medium">{item.repositories}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Using since</p>
                      <p className="font-medium">{item.usingSince}</p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="codeQuality">
          <Card className="shadow-sm">
            <CardHeader className="bg-gray-50">
              <CardTitle>Code Quality</CardTitle>
            </CardHeader>
            <CardContent>
              {codeQualityData.map((item, index) => (
                <div key={index} className="mb-8 pb-6 border-b last:border-0">
                  <h3 className="text-xl font-semibold mb-4">{item.language}</h3>
                  <div className="grid grid-cols-2 gap-6 mb-4">
                    <div className="flex items-center">
                      <p className="text-sm text-gray-500 mr-2">Reliability Rating:</p>
                      <Badge className={`${getRatingColor(item.reliabilityRating)}`}>
                        {item.reliabilityRating}
                      </Badge>
                    </div>
                    <div className="flex items-center">
                      <p className="text-sm text-gray-500 mr-2">Security Rating:</p>
                      <Badge className={`${getRatingColor(item.securityRating)}`}>
                        {item.securityRating}
                      </Badge>
                    </div>
                    <div className="flex items-center">
                      <p className="text-sm text-gray-500 mr-2">Maintainability Rating:</p>
                      <Badge className={`${getRatingColor(item.maintainabilityRating)}`}>
                        {item.maintainabilityRating}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Duplicated Lines Density:</p>
                      <p className="font-medium">{item.duplicatedLinesDensity}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Vulnerability per commit:</p>
                      <p className="font-medium">{item.vulnerabilityPerCommit}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Bugs per commit:</p>
                      <p className="font-medium">{item.bugsPerCommit}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Code Smells per commit:</p>
                      <p className="font-medium">{item.codeSmellsPerCommit}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Complexity per commit:</p>
                      <p className="font-medium">{item.complexityPerCommit}</p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}